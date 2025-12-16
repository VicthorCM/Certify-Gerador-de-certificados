# 🎓 CertifyMe - Sistema Emissor e Validador de Certificados

Sistema desenvolvido em Django para automatizar a emissão de certificados corporativos/educacionais, com foco em segurança e performance.

## 🚀 Funcionalidades
- **Emissão em Lote:** Processamento de planilhas Excel/CSV com Pandas.
- **Geração de PDF:** Engine gráfica com ReportLab (não é apenas conversão HTML).
- **Validação Anti-Fraude:** Cada certificado possui um UUID único e QR Code verificável.
- **Download Otimizado:** Entrega de múltiplos arquivos compactados em ZIP.

## 🛠 Tecnologias
- **Backend:** Python, Django 5.
- **Processamento de Dados:** Pandas, OpenPyXL.
- **Arquivos:** ReportLab (PDF), QRCode, ZipFile.
- **Frontend:** Django Templates + Bootstrap 5.

## 📸 Screenshots
*( print da tela de upload e print do PDF gerado)*

## ⚙️ Como rodar localmente
1. Clone o repositório.
2. Crie um ambiente virtual: `python -m venv venv`
3. Instale as dependências: `pip install -r requirements.txt`
4. Crie um arquivo `.env` baseado no exemplo.
5. Execute as migrações: `python manage.py migrate`
6. Rode o servidor: `python manage.py runserver`