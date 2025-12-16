from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    
    list_display = ('student_name', 'course_name', 'created_at', 'is_valid')
    
   
    list_filter = ('is_valid', 'course_name', 'created_at')
    
   
    search_fields = ('student_name', 'token')
    
    
    readonly_fields = ('uu_id',)