import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [oauthLoading, setOauthLoading] = useState(false);
  const { login } = useAuth();

  const handleOAuthLogin = async () => {
    setError('');
    setOauthLoading(true);
    try {
      const response = await api.get('/auth/oauth/login/');
      const { authorization_url, state, code_verifier } = response.data;

      if (state) sessionStorage.setItem('oauth_state', state);
      if (code_verifier) sessionStorage.setItem('oauth_code_verifier', code_verifier);

      if (authorization_url && authorization_url.includes('plac-mvp-client-id')) {
        setError('O SSO Corporativo aguarda o registro oficial do Client ID no Azure/Entra ID da Telebras. Por favor, utilize o acesso com as credenciais de homologação abaixo.');
        setOauthLoading(false);
        return;
      }

      if (authorization_url) {
        window.location.href = authorization_url;
      } else {
        setError('URL de autorização do Provedor de Identidade não configurada.');
      }
    } catch (err) {
      console.error('Falha ao iniciar autenticação OAuth:', err);
      setError('Não foi possível conectar ao provedor corporativo SSO.');
    } finally {
      setOauthLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
    } catch (err) {
      setError('Falha no login. Verifique suas credenciais.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-slate-800 rounded-xl shadow-lg border border-slate-700 p-8">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-blue-600/20 text-blue-400 mb-3 border border-blue-500/30">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-wide">Sistema de Gestão PLAC</h1>
          <p className="text-slate-400 text-sm mt-1">Acesso Seguro & Governança de Contratações</p>
        </div>

        {error && (
          <div className="mb-5 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        {/* Botão de Login Corporativo SSO */}
        <div className="mb-6">
          <button
            type="button"
            onClick={handleOAuthLogin}
            disabled={oauthLoading || loading}
            className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:opacity-50 text-white font-semibold rounded-lg shadow-lg flex items-center justify-center gap-3 transition duration-200 border border-blue-400/30"
          >
            {oauthLoading ? (
              <div className="inline-block animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
            )}
            <span>Entrar com SSO Corporativo (OAuth 2.0)</span>
          </button>
          <p className="text-center text-[11px] text-slate-400 mt-2">
            Compatível com Entra ID (Telebras), Gov.br e Keycloak
          </p>
        </div>

        <div className="relative flex py-2 items-center mb-6">
          <div className="flex-grow border-t border-slate-700"></div>
          <span className="flex-shrink mx-4 text-xs uppercase tracking-wider text-slate-500 font-medium">
            ou credenciais de homologação
          </span>
          <div className="flex-grow border-t border-slate-700"></div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Usuário</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
              placeholder="Ex: demandante, diretor, analista_gcc..."
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">Senha</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition text-sm"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading || oauthLoading}
            className="w-full py-2.5 px-4 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white font-bold rounded-lg shadow transition duration-200 text-sm"
          >
            {loading ? 'Autenticando...' : 'Acessar com Senha Local'}
          </button>
        </form>

        <div className="mt-5 p-3.5 bg-slate-900/90 border border-slate-700/80 rounded-xl text-xs space-y-2 text-slate-300">
          <div className="font-bold text-slate-200 flex items-center justify-between">
            <span>🔑 Acesso Rápido de Homologação:</span>
            <span className="text-[10px] text-amber-400 font-mono">Senha: admin123</span>
          </div>
          <div className="grid grid-cols-2 gap-1.5 pt-1 text-[11px]">
            <button
              type="button"
              onClick={() => { setUsername('admin'); setPassword('admin123'); }}
              className="py-1.5 px-2.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 text-left transition flex items-center gap-1.5"
            >
              <span>👑</span>
              <span><strong>admin</strong></span>
            </button>
            <button
              type="button"
              onClick={() => { setUsername('diretor'); setPassword('diretor123'); }}
              className="py-1.5 px-2.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 text-left transition flex items-center gap-1.5"
            >
              <span>⚖️</span>
              <span><strong>diretor</strong></span>
            </button>
            <button
              type="button"
              onClick={() => { setUsername('demandante'); setPassword('demandante123'); }}
              className="py-1.5 px-2.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 text-left transition flex items-center gap-1.5"
            >
              <span>📝</span>
              <span><strong>demandante</strong></span>
            </button>
            <button
              type="button"
              onClick={() => { setUsername('dafri'); setPassword('dafri123'); }}
              className="py-1.5 px-2.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white border border-slate-700 text-left transition flex items-center gap-1.5"
            >
              <span>🏛️</span>
              <span><strong>dafri</strong></span>
            </button>
          </div>
        </div>

        <div className="mt-4 text-[11px] text-slate-500 border-t border-slate-700/60 pt-3 text-center">
          Perfis suportados: Demandante, Diretor, GCC, DAFRI, Diretoria Executiva
        </div>
      </div>
    </div>
  );
}
