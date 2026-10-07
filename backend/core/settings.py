import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'plac-insecure-mvp-secret-key-development-mode-2026')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Bibliotecas de Terceiros
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Apps do Sistema PLAC
    'users',
    'demands',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

import sys

# Configuração do Banco de Dados PostgreSQL (ou SQLite em modo de teste)
if 'test' in sys.argv or os.environ.get('USE_SQLITE') == '1':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        },
        'pncp': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'plac_db'),
            'USER': os.environ.get('DB_USER', 'plac_user'),
            'PASSWORD': os.environ.get('DB_PASS', 'plac_password'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        },
        'pncp': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'pncp_db',
            'USER': 'user',
            'PASSWORD': 'password',
            'HOST': 'pncp_db',
            'PORT': '5432',
        }
    }


# Usuário Customizado com Role
AUTH_USER_MODEL = 'users.User'

# Django REST Framework & JWT
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# CORS
CORS_ALLOW_ALL_ORIGINS = True

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações OAuth 2.0 / OpenID Connect (OIDC)
OAUTH_CLIENT_ID = os.environ.get('OAUTH_CLIENT_ID', 'plac-mvp-client-id')
OAUTH_CLIENT_SECRET = os.environ.get('OAUTH_CLIENT_SECRET', 'plac-mvp-client-secret')
OAUTH_AUTH_URL = os.environ.get('OAUTH_AUTH_URL', 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize')
OAUTH_TOKEN_URL = os.environ.get('OAUTH_TOKEN_URL', 'https://login.microsoftonline.com/common/oauth2/v2.0/token')
OAUTH_USERINFO_URL = os.environ.get('OAUTH_USERINFO_URL', 'https://graph.microsoft.com/oidc/userinfo')
OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:3030/oauth/callback')
OAUTH_PROVIDER_NAME = os.environ.get('OAUTH_PROVIDER_NAME', 'TELEBRAS_ENTRA_ID')
OAUTH_SCOPE = os.environ.get('OAUTH_SCOPE', 'openid profile email')

