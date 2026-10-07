import base64
import hashlib
import json
import os
import secrets
import urllib.parse
import urllib.request
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def generate_pkce_pair():
    """
    Gera par PKCE:
    - code_verifier: string pseudoaleatória segura (base64url)
    - code_challenge: hash SHA-256 do verifier codificado em base64url sem padding
    """
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge


def generate_state():
    """Gera token aleatório para mitigação de ataques CSRF."""
    return secrets.token_hex(16)


def get_authorization_url(state=None, code_challenge=None):
    """
    Constrói a URL de autorização do IdP corporativo com PKCE e state.
    """
    state = state or generate_state()
    auth_base = getattr(settings, 'OAUTH_AUTH_URL', '')
    client_id = getattr(settings, 'OAUTH_CLIENT_ID', '')
    redirect_uri = getattr(settings, 'OAUTH_REDIRECT_URI', '')
    scope = getattr(settings, 'OAUTH_SCOPE', 'openid profile email')

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'redirect_uri': redirect_uri,
        'scope': scope,
        'state': state,
        'response_mode': 'query',
    }

    if code_challenge:
        params['code_challenge'] = code_challenge
        params['code_challenge_method'] = 'S256'

    query_string = urllib.parse.urlencode(params)
    url = f"{auth_base}?{query_string}" if auth_base else ""
    return url, state


def exchange_code_for_token(code: str, code_verifier: str = None) -> dict:
    """
    Efetua a troca do authorization code pelo token junto ao IdP.
    """
    token_url = getattr(settings, 'OAUTH_TOKEN_URL', '')
    client_id = getattr(settings, 'OAUTH_CLIENT_ID', '')
    client_secret = getattr(settings, 'OAUTH_CLIENT_SECRET', '')
    redirect_uri = getattr(settings, 'OAUTH_REDIRECT_URI', '')

    payload = {
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': redirect_uri,
    }

    if code_verifier:
        payload['code_verifier'] = code_verifier

    req = urllib.request.Request(token_url, data=urllib.parse.urlencode(payload).encode('utf-8'))
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))


def get_user_info(access_token: str) -> dict:
    """
    Obtém informações do usuário via endpoint UserInfo do IdP.
    """
    userinfo_url = getattr(settings, 'OAUTH_USERINFO_URL', '')
    headers = {'Authorization': f'Bearer {access_token}'}
    req = urllib.request.Request(userinfo_url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode('utf-8'))


def map_claims_to_role(claims: dict) -> str:
    """
    Mapeia grupos/claims corporativas para os papéis de negócio do PLAC:
    - DEMANDANTE
    - DIRETOR
    - ANALISTA_GCC
    - DIRETOR_DAFRI
    - DIRETORIA_EXECUTIVA
    """
    groups = claims.get('groups', []) or claims.get('roles', [])
    if isinstance(groups, str):
        groups = [groups]

    groups_lower = [str(g).lower() for g in groups]
    job_title = str(claims.get('job_title', '') or claims.get('title', '')).lower()
    dept = str(claims.get('department', '') or claims.get('lotacao', '')).lower()

    if any('dafri' in g for g in groups_lower) or 'dafri' in dept:
        return 'DIRETOR_DAFRI'
    if any('executiva' in g or 'diretoria' in g for g in groups_lower) or 'diretor executivo' in job_title:
        return 'DIRETORIA_EXECUTIVA'
    if any('gcc' in g or 'compras' in g or 'licitacao' in g for g in groups_lower) or 'gcc' in dept:
        return 'ANALISTA_GCC'
    if any('diretor' in g for g in groups_lower) or 'diretor' in job_title:
        return 'DIRETOR'

    return 'DEMANDANTE'


def provision_oauth_user(user_info: dict, provider_name: str = None) -> dict:
    """
    Realiza o provisionamento Just-in-Time (JIT) do usuário corporativo e emite
    o par de tokens JWT (SimpleJWT) da aplicação.
    """
    provider = provider_name or getattr(settings, 'OAUTH_PROVIDER_NAME', 'OIDC')
    sub = user_info.get('sub') or user_info.get('id')
    if not sub:
        raise ValueError("IdP userinfo não forneceu claim 'sub' ou identificador único.")

    email = user_info.get('email', '')
    preferred_username = user_info.get('preferred_username', '')
    name = user_info.get('name', '') or user_info.get('given_name', '')
    dept = user_info.get('department') or user_info.get('lotacao', '')

    username = preferred_username or (email.split('@')[0] if email else f"user_{sub[:8]}")
    role = map_claims_to_role(user_info)

    # Localiza por sub ou username/email
    user = User.objects.filter(oauth_sub=str(sub)).first()
    if not user and email:
        user = User.objects.filter(email__iexact=email).first()
    if not user:
        user = User.objects.filter(username__iexact=username).first()

    if user:
        user.oauth_sub = str(sub)
        user.oauth_provider = provider
        if email and not user.email:
            user.email = email
        if name and not user.first_name:
            user.first_name = name
        if dept:
            user.department = dept
        # Mantém role se já personalizada, ou atualiza se DEMANDANTE
        if user.role == 'DEMANDANTE' and role != 'DEMANDANTE':
            user.role = role
        user.save()
    else:
        user = User.objects.create(
            username=username,
            email=email,
            first_name=name,
            role=role,
            oauth_provider=provider,
            oauth_sub=str(sub),
            department=dept,
        )

    # Emite tokens JWT compatíveis com o ecossistema existente
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['username'] = user.username

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'department': user.department,
        }
    }
