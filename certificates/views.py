import io
from django.http import FileResponse, HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from .models import Certificate
from django.shortcuts import render, redirect
import pandas as pd
from .forms import UploadCertificatesForm
from django.contrib import messages
import zipfile
from django.contrib.auth.decorators import login_required
from core import settings
import os
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.views.generic import CreateView
from django.urls import reverse_lazy


class CreateUser(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "register.html"
    success_url= reverse_lazy("home")

def home(request):
    return render(request,'home.html',{})

@login_required(login_url='/login/')
def generate_pdf(request, certificate_id):
    # 1. Busca os dados no banco (ou retorna erro 404 se não achar)
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    pdf_bytes = generate_pdf_bytes(certificate)

    # 2. Cria um buffer de memória (arquivo virtual)
    buffer = io.BytesIO(pdf_bytes)
    
    return FileResponse(buffer, as_attachment=False, filename=f"certificado_{certificate.student_name}.pdf")

def generate_pdf_bytes(certificate):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    largura, altura = landscape(A4) # A4 Paisagem: aprox 841 x 595 pontos

    # --- 1. CONFIGURAÇÃO DE ASSETS (Caminhos) ---
    # Idealmente, use settings.BASE_DIR para achar os arquivos
    static_path = os.path.join(settings.BASE_DIR, 'static')
    
    bg_path = os.path.join(static_path, 'img', 'certificado_bg.jpg')
    font_path = os.path.join(static_path, 'fonts', 'GreatVibes-Regular.ttf')

    # --- 2. REGISTRANDO FONTE CUSTOMIZADA ---
    # Só funciona se você tiver baixado o arquivo .ttf
    try:
        pdfmetrics.registerFont(TTFont('Cursiva', font_path))
        fonte_nome = 'Cursiva'
    except:
        fonte_nome = 'Helvetica-Bold' # Fallback se não achar a fonte

    # --- 3. DESENHANDO O FUNDO ---
    # O fundo deve ser a PRIMEIRA coisa, para ficar atrás de tudo
    try:
        # width e height forçam a imagem a ocupar a página toda
        pdf.drawImage(bg_path, 0, 0, width=largura, height=altura)
    except:
        pass # Se não achar a imagem, fica branco mesmo

    # --- 4. TÍTULO E CORPO ---
    
    # Título (Centralizado)
    pdf.setFont("Helvetica-Bold", 36)
    pdf.setFillColorRGB(0.2, 0.2, 0.2) # Cinza escuro (mais elegante que preto puro)
    titulo = "CERTIFICADO DE CONCLUSÃO"
    w_titulo = pdf.stringWidth(titulo, "Helvetica-Bold", 36)
    pdf.drawString((largura - w_titulo)/2, altura - 140, titulo)

    # Texto introdutório
    pdf.setFont("Helvetica", 14)
    texto_intro = "Certificamos que, para os devidos fins, que"
    w_intro = pdf.stringWidth(texto_intro, "Helvetica", 14)
    pdf.drawString((largura - w_intro)/2, altura - 200, texto_intro)

    # NOME DO ALUNO (O destaque visual)
    pdf.setFont(fonte_nome, 60) # Fonte cursiva grande
    nome = certificate.student_name
    w_nome = pdf.stringWidth(nome, fonte_nome, 60)
    pdf.drawString((largura - w_nome)/2, altura - 270, nome)

    # Texto do Curso
    pdf.setFont("Helvetica", 16)
    texto_curso = f"Concluiu com êxito o curso de {certificate.course_name}"
    w_curso = pdf.stringWidth(texto_curso, "Helvetica", 16)
    pdf.drawString((largura - w_curso)/2, altura - 330, texto_curso)

    # --- 5. ASSINATURA E CARGO (NOVO) ---
    # Linha da assinatura
    pdf.setLineWidth(1)
    pdf.line(largura/2 - 100, 130, largura/2 + 100, 130) # Linha centralizada embaixo

    # Nome do Instrutor
    pdf.setFont("Helvetica-Bold", 12)
    instrutor = certificate.instructor_name
    w_instr = pdf.stringWidth(instrutor, "Helvetica-Bold", 12)
    pdf.drawString((largura - w_instr)/2, 115, instrutor)

    # Cargo
    pdf.setFont("Helvetica", 10)
    cargo = certificate.instructor_role
    w_cargo = pdf.stringWidth(cargo, "Helvetica", 10)
    pdf.setFillColorRGB(0.5, 0.5, 0.5) # Cinza mais claro
    pdf.drawString((largura - w_cargo)/2, 100, cargo)

    # --- 6. QR CODE E DATA ---
    # Data no canto esquerdo
    pdf.setFillColorRGB(0, 0, 0)
    pdf.setFont("Helvetica", 10)
    data_texto = f"Emitido em: {certificate.created_at.strftime('%d/%m/%Y')}"
    pdf.drawString(50, 50, data_texto)

    # QR Code no canto direito
    link = f"https://certify-gerador-de-certificados.onrender.com/validar/{certificate.uu_id}"
    qr = qrcode.make(link)
    qr_img = ImageReader(qr.get_image())
    pdf.drawImage(qr_img, largura - 110, 40, width=70, height=70)

    pdf.showPage()
    pdf.save()
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


@login_required(login_url='/login/')
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


