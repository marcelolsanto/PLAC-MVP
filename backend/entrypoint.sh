#!/bin/sh

echo "Aguardando o banco de dados inicializar..."
sleep 2

echo "Aplicando migrações..."
python manage.py makemigrations users demands
python manage.py migrate

echo "Criando usuários de demonstração..."
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()

users = [
    ('demandante', 'demandante@plac.gov.br', 'DEMANDANTE'),
    ('diretor', 'diretor@plac.gov.br', 'DIRETOR'),
    ('analista_gcc', 'gcc@plac.gov.br', 'ANALISTA_GCC'),
    ('diretoria_executiva', 'executiva@plac.gov.br', 'DIRETORIA_EXECUTIVA'),
]

for username, email, role in users:
    if not User.objects.filter(username=username).exists():
        u = User.objects.create_user(username=username, email=email, password='password123', role=role)
        print(f'Usuário {username} ({role}) criado com sucesso.')
"

echo "Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
