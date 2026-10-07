import base64
import hashlib
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.services_oauth import (
    exchange_code_for_token,
    generate_pkce_pair,
    generate_state,
    get_authorization_url,
    get_user_info,
    map_claims_to_role,
    provision_oauth_user,
)

User = get_user_model()


class OAuthServicesTestCase(TestCase):
    def test_pkce_generation(self):
        verifier, challenge = generate_pkce_pair()
        self.assertTrue(len(verifier) >= 43)
        self.assertTrue(len(challenge) > 20)

        # Validação do algoritmo S256
        expected_digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        expected_challenge = base64.urlsafe_b64encode(expected_digest).decode('utf-8').rstrip('=')
        self.assertEqual(challenge, expected_challenge)

    def test_generate_state(self):
        state1 = generate_state()
        state2 = generate_state()
        self.assertNotEqual(state1, state2)
        self.assertEqual(len(state1), 32)

    def test_get_authorization_url(self):
        verifier, challenge = generate_pkce_pair()
        url, state = get_authorization_url(code_challenge=challenge)
        self.assertIn("client_id=", url)
        self.assertIn("response_type=code", url)
        self.assertIn("code_challenge=", url)
        self.assertIn("code_challenge_method=S256", url)
        self.assertIn(f"state={state}", url)

    def test_role_mapping(self):
        self.assertEqual(map_claims_to_role({'groups': ['GCC_OPERACIONAL']}), 'ANALISTA_GCC')
        self.assertEqual(map_claims_to_role({'roles': ['DIRETOR_TECNICO']}), 'DIRETOR')
        self.assertEqual(map_claims_to_role({'department': 'DAFRI / Assessoria'}), 'DIRETOR_DAFRI')
        self.assertEqual(map_claims_to_role({'groups': ['Diretoria Executiva']}), 'DIRETORIA_EXECUTIVA')
        self.assertEqual(map_claims_to_role({'department': 'GERENCIA_LOGISTICA'}), 'DEMANDANTE')

    def test_provision_oauth_user_jit_new(self):
        user_info = {
            'sub': 'entra-id-sub-12345',
            'email': 'analista.compras@telebras.com.br',
            'preferred_username': 'analista.compras',
            'name': 'Carlos Silva',
            'groups': ['GCC_ANALISTA'],
            'department': 'GCC',
        }
        auth_data = provision_oauth_user(user_info)

        self.assertIn('access', auth_data)
        self.assertIn('refresh', auth_data)
        self.assertEqual(auth_data['user']['username'], 'analista.compras')
        self.assertEqual(auth_data['user']['role'], 'ANALISTA_GCC')

        # Verifica persistência no banco
        user = User.objects.get(oauth_sub='entra-id-sub-12345')
        self.assertEqual(user.email, 'analista.compras@telebras.com.br')
        self.assertEqual(user.first_name, 'Carlos Silva')
        self.assertEqual(user.role, 'ANALISTA_GCC')

    def test_provision_oauth_user_jit_update_existing(self):
        user = User.objects.create(
            username='carlos.silva',
            email='carlos.silva@telebras.com.br',
            role='DEMANDANTE',
        )
        user_info = {
            'sub': 'sub-999-new',
            'email': 'carlos.silva@telebras.com.br',
            'name': 'Carlos Silva Atualizado',
            'groups': ['DIRETOR_DEMANDANTE'],
        }
        auth_data = provision_oauth_user(user_info)
        user.refresh_from_db()

        self.assertEqual(user.oauth_sub, 'sub-999-new')
        self.assertEqual(user.role, 'DIRETOR')
        self.assertEqual(auth_data['user']['role'], 'DIRETOR')


class OAuthEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_oauth_login_init_endpoint(self):
        response = self.client.get('/api/auth/oauth/login/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn('authorization_url', data)
        self.assertIn('state', data)
        self.assertIn('code_verifier', data)
        self.assertTrue(len(data['code_verifier']) > 30)

    @patch('users.views.exchange_code_for_token')
    @patch('users.views.get_user_info')
    def test_oauth_callback_endpoint_success(self, mock_get_user_info, mock_exchange):
        mock_exchange.return_value = {
            'access_token': 'mock-access-token-123',
            'token_type': 'Bearer',
        }
        mock_get_user_info.return_value = {
            'sub': 'sub-telebras-777',
            'email': 'marina.diretoria@telebras.com.br',
            'name': 'Marina Souza',
            'groups': ['DIRETORIA_EXECUTIVA'],
        }

        payload = {
            'code': 'mock_auth_code_xyz',
            'code_verifier': 'mock_verifier_abc123',
        }
        response = self.client.post('/api/auth/oauth/callback/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn('access', data)
        self.assertIn('refresh', data)
        self.assertEqual(data['user']['role'], 'DIRETORIA_EXECUTIVA')
        self.assertEqual(data['user']['email'], 'marina.diretoria@telebras.com.br')

    def test_oauth_callback_missing_code(self):
        response = self.client.post('/api/auth/oauth/callback/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.json())

    @patch('users.views.exchange_code_for_token')
    def test_oauth_callback_idp_failure(self, mock_exchange):
        mock_exchange.side_effect = Exception("Conexão recusada pelo Provedor OIDC")

        payload = {
            'code': 'invalid_code',
            'code_verifier': 'verifier_123',
        }
        response = self.client.post('/api/auth/oauth/callback/', payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Falha na autenticação corporativa', response.json()['error'])
