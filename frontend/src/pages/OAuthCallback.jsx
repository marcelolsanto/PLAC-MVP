import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function OAuthCallback() {
  const [status, setStatus] = useState('Processando autenticação corporativa...');
  const [error, setError] = useState(null);
  const { handleAuthSuccess } = useAuth();

  useEffect(() => {
    async function processCallback() {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      const state = urlParams.get('state');
      const oauthError = urlParams.get('error') || urlParams.get('error_description');

      if (oauthError) {
        setError(`O provedor de identidade retornou um erro: ${oauthError}`);
        return;
      }

      if (!code) {
        setError('Nenhum código de autorização encontrado na URL.');
        return;
      }

      const storedState = sessionStorage.getItem('oauth_state');
      const codeVerifier = sessionStorage.getItem('oauth_code_verifier');

      if (storedState && state && storedState !== state) {
        setError('Falha de segurança na validação do estado (State mismatch). Possível ataque CSRF.');
        return;
      }

      try {
        setStatus('Validando credenciais e sincronizando perfil corporativo...');
        const response = await api.post('/auth/oauth/callback/', {
          code,
          code_verifier: codeVerifier,
          state,
        });

        sessionStorage.removeItem('oauth_state');
        sessionStorage.removeItem('oauth_code_verifier');

        handleAuthSuccess(response.data);
        setStatus('Autenticado com sucesso! Redirecionando...');

        window.location.href = '/';
      } catch (err) {
        console.error('Erro na validação do callback OAuth:', err);
        const errorMsg = err.response?.data?.error || 'Não foi possível concluir a autenticação corporativa.';
        setError(errorMsg);
      }
    }

    processCallback();
  }, [handleAuthSuccess]);

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800 rounded-xl shadow-lg border border-slate-700 p-8 text-center">
        <h2 className="text-xl font-bold text-white mb-4">Autenticação Corporativa PLAC</h2>

        {error ? (
          <div>
            <div className="p-4 mb-6 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm">
              {error}
            </div>
            <a
              href="/"
              className="inline-block py-2.5 px-6 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition"
            >
              Voltar para o Login
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="inline-block animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
            <p className="text-slate-300 text-sm">{status}</p>
          </div>
        )}
      </div>
    </div>
  );
}
