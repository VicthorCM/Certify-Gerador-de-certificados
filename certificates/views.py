import io
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
import qrcode
from .models import Certificate
from django.shortcuts import render, redirect
import pandas as pd
from .forms import UploadCertificatesForm
from django.contrib import messages
import zipfile

def generate_pdf(request, certificate_id):
    # 1. Busca os dados no banco (ou retorna erro 404 se não achar)
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    pdf_bytes = generate_pdf_bytes(certificate)

    # 2. Cria um buffer de memória (arquivo virtual)
    buffer = io.BytesIO(pdf_bytes)
    
    return FileResponse(buffer, as_attachment=False, filename=f"certificado_{certificate.student_name}.pdf")

def generate_pdf_bytes(certificate):
    
    buffer = io.BytesIO()
    # 3. Cria o objeto Canvas (a "tela" de pintura do PDF)
    # landscape(A4) deixa a folha deitada
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    largura, altura = landscape(A4)

    # --- DESENHANDO O CONTEÚDO ---
    
    # Título
    pdf.setFont("Helvetica-Bold", 30)
    texto_titulo = "CERTIFICADO DE CONCLUSÃO"
    # Lógica para centralizar: (Largura da Pág - Largura do Texto) / 2
    largura_texto = pdf.stringWidth(texto_titulo, "Helvetica-Bold", 30)
    pdf.drawString((largura - largura_texto) / 2, altura - 150, texto_titulo)
    
    # Texto Principal
    pdf.setFont("Helvetica", 18)
    texto_corpo = f"Certificamos que {certificate.student_name} concluiu o curso"
    largura_texto = pdf.stringWidth(texto_corpo, "Helvetica", 18)
    pdf.drawString((largura - largura_texto) / 2, altura - 250, texto_corpo)
    
    # Nome do Curso (Destaque)
    pdf.setFont("Helvetica-Bold", 24)
    texto_curso = certificate.course_name
    largura_texto = pdf.stringWidth(texto_curso, "Helvetica-Bold", 24)
    pdf.drawString((largura - largura_texto) / 2, altura - 290, texto_curso)

    # --- GERANDO O QR CODE ---
    
    # URL que o QR Code vai abrir (ajuste o domínio depois)
    # Por enquanto usamos localhost
    link_validacao = f"http://127.0.0.1:8000/validar/{certificate.uu_id}"
    
    qr = qrcode.make(link_validacao)
    qr_img = ImageReader(qr.get_image())
    
    # Desenha o QR Code no canto inferior direito
    # drawImage(imagem, X, Y, largura, altura)
    pdf.drawImage(qr_img, largura - 120, 30, width=80, height=80)
    
    # Texto explicativo embaixo do QR
    pdf.setFont("Helvetica", 8)
    pdf.drawString(largura - 120, 20, "Valide a autenticidade")

    # Finaliza o PDF
    pdf.showPage()
    pdf.save()
    
    # Retorna o arquivo para download
    buffer.seek(0)
    return buffer.getvalue()

def validate(request, uu_id):
    try:
        
        certificate = Certificate.objects.get(uu_id=uu_id, is_valid=True)
        context = {
            'valid': True,
            'certificate': certificate
        }
    except Certificate.DoesNotExist:
       
        context = {
            'valid': False
        }
    
    return render(request, 'validate.html', context)



def upload(request):
    if request.method == 'POST':
       
        form = UploadCertificatesForm(request.POST, request.FILES)
        
        if form.is_valid():
          
            arquivo = form.cleaned_data['arquivo']
            
            try:
                
                if arquivo.name.endswith('.xlsx'):
                    df = pd.read_excel(arquivo)
                elif arquivo.name.endswith('.csv'):
                    df = pd.read_csv(arquivo)
                else:
                   
                    messages.error(request, "Formato inválido.")
                    return render(request, 'upload.html', {'form': form})

                certificates_to_save = []
                
                zip_buffer = io.BytesIO()

                with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                    for index, row in df.iterrows():
                        obj = Certificate.objects.create(
                            student_name=row['Nome'],
                            student_email=row.get('Email', ''),
                            course_name=row['Curso']
                        )
                        certificates_to_save.append(obj)

                        pdf_bytes = generate_pdf_bytes(obj)
                        
                        nome_arquivo = f"{obj.student_name.replace(' ', '_')}.pdf"
                        
                        zip_file.writestr(nome_arquivo, pdf_bytes)
                    
                    
                zip_buffer.seek(0)
                response = HttpResponse(zip_buffer, content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="certificados_gerados.zip"'
                messages.success(request, f"{len(certificates_to_save)} certificados importados!")
                return response

            except Exception as e:
                messages.error(request, f"Erro ao processar arquivo: {str(e)}")

    else:
       
        form = UploadCertificatesForm()

    
    return render(request, 'upload.html', {'form': form})