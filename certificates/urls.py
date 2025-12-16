from .views import *
from django.urls import path
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('home/',home,name='home'),
    path('create/<int:certificate_id>', generate_pdf,name = "gerar_pdf" ),
    path('validar/<str:uu_id>',validate, name='validate_certificate'),
    path('upload/',upload,name='upload'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/',CreateUser.as_view(),name='user_register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
