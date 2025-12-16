from django.db import models
import uuid
class Certificate(models.Model):
    student_name = models.CharField("Nome do Aluno", max_length=255)
    student_email = models.EmailField("E-mail do Aluno", blank=True, null=True)
    course_name = models.CharField("Nome do Curso", max_length=255)
    instructor_name = models.CharField("Nome do Instrutor", max_length=255, default=" ")
    instructor_role = models.CharField("Cargo", max_length=255, default="Coordenador (a)")

    created_at = models.DateTimeField("Criado em", auto_now_add=True)

    is_valid = models.BooleanField(default=True)

    
    uu_id = models.UUIDField(default=uuid.uuid4,editable=False, unique=True)
     
    class Meta:
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"
        ordering = ['-created_at'] 

    def __str__(self):
        return f"{self.student_name} - {self.course_name}"
    

