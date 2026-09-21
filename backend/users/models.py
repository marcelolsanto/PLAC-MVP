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

    def __str__(self):
        return f"{self.username} - {self.role}"
