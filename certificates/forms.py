from django import forms

from .models import Certificate



class CertificateForm(forms.ModelForm):
    class Meta:
        model= Certificate
        fields = ['student_name','student_email','course_name']

class UploadCertificatesForm(forms.Form):
   
    arquivo = forms.FileField(label="Selecione a planilha (.xlsx ou .csv)")
    
    
    def clean_arquivo(self):
        arquivo = self.cleaned_data['arquivo']
        if not arquivo.name.endswith('.xlsx') and not arquivo.name.endswith('.csv'):
            raise forms.ValidationError("Por favor, envie apenas arquivos Excel (.xlsx) ou CSV.")
        return arquivo