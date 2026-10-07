from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('DEMANDANTE', 'Representante da Área Demandante'),
        ('DIRETOR', 'Diretor(a) da Área Requisitante'),
        ('ANALISTA_GCC', 'Analista da GCC'),
        ('DIRETOR_DAFRI', 'Diretor(a) da DAFRI'),
        ('DIRETORIA_EXECUTIVA', 'Diretoria Executiva'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='DEMANDANTE')
    oauth_provider = models.CharField(max_length=50, blank=True, null=True, help_text="Provedor OAuth (ex: TELEBRAS_ENTRA_ID, GOV_BR)")
    oauth_sub = models.CharField(max_length=255, blank=True, null=True, unique=True, help_text="Subject ID único retornado pelo IdP")
    department = models.CharField(max_length=100, blank=True, null=True, help_text="Lotação ou departamento corporativo")

    def __str__(self):
        return f"{self.username} - {self.role}"

