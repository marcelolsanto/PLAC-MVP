import logging
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import CustomTokenObtainPairSerializer
from .services_oauth import (
    exchange_code_for_token,
    generate_pkce_pair,
    generate_state,
    get_authorization_url,
    get_user_info,
    provision_oauth_user,
)

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class OAuthLoginInitView(APIView):
    """
    Inicia o fluxo OAuth 2.0 com PKCE.
    Retorna a URL de autorização do IdP, o state e o code_verifier gerados.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        code_verifier, code_challenge = generate_pkce_pair()
        state = generate_state()
        auth_url, _ = get_authorization_url(state=state, code_challenge=code_challenge)

        return Response({
            'authorization_url': auth_url,
            'state': state,
            'code_verifier': code_verifier,
        }, status=status.HTTP_200_OK)


class OAuthCallbackView(APIView):
    """
    Recebe o authorization code após o redirecionamento do IdP,
    valida o code_verifier (PKCE), obtém o userinfo e provisiona o usuário (JIT),
    retornando os tokens SimpleJWT (access, refresh).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        code = request.data.get('code')
        code_verifier = request.data.get('code_verifier')

        if not code:
            return Response(
                {'error': 'Parâmetro obrigatório ausente: code.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token_response = exchange_code_for_token(code=code, code_verifier=code_verifier)
            access_token = token_response.get('access_token')

            if not access_token:
                return Response(
                    {'error': 'Falha na resposta do IdP: access_token não fornecido.'},
                    status=status.HTTP_502_BAD_GATEWAY
                )

            # Se o IdP já retornar claims decodificadas no id_token ou via UserInfo
            user_info = get_user_info(access_token)
            auth_payload = provision_oauth_user(user_info)

            return Response(auth_payload, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception("Erro no callback OAuth: %s", str(e))
            return Response(
                {'error': f'Falha na autenticação corporativa: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
