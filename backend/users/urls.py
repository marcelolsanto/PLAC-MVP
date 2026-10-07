from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    OAuthLoginInitView,
    OAuthCallbackView,
)

urlpatterns = [
    # Autenticação Local / Legado (Simulação e Homologação)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Autenticação Corporativa OAuth 2.0 / OIDC
    path('auth/oauth/login/', OAuthLoginInitView.as_view(), name='oauth_login_init'),
    path('auth/oauth/callback/', OAuthCallbackView.as_view(), name='oauth_callback'),
]
