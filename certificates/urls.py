from .views import *
from django.urls import path
urlpatterns = [
    path('create/<int:certificate_id>', generate_pdf,name = "gerar_pdf" ),
    path('validar/<str:uu_id>',validate, name='validate_certificate'),
    path('upload/',upload,name='upload')
]
