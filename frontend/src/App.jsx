import React, { Component } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import OAuthCallback from './pages/OAuthCallback';


class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('CRITICAL REACT RENDER ERROR:', error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-900 text-white p-8 flex flex-col items-center justify-center font-sans">
          <div className="max-w-2xl w-full bg-red-950/80 border border-red-500 rounded-xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-3">
              <span className="text-3xl">⚠️</span>
              <div>
                <h1 className="text-xl font-bold text-red-300">Falha de Renderização na Interface</h1>
                <p className="text-xs text-red-200">Um erro de componente foi interceptado pelo Guardião do PLAC.</p>
              </div>
            </div>
            <div className="bg-slate-900/90 p-4 rounded-lg border border-red-900 font-mono text-xs text-red-300 overflow-x-auto">
              <p className="font-bold">{this.state.error?.toString()}</p>
              {this.state.errorInfo?.componentStack && (
                <pre className="mt-2 text-[11px] text-slate-400 whitespace-pre-wrap">
                  {this.state.errorInfo.componentStack}
                </pre>
              )}
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg transition"
              >
                Recarregar Página
              </button>
              <button
                type="button"
                onClick={() => {
                  localStorage.clear();
                  window.location.reload();
                }}
                className="px-4 py-2 bg-red-800 hover:bg-red-700 text-white text-xs font-bold rounded-lg transition"
              >
                Limpar Sessão / Reautenticar
              </button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function MainRouter() {
  const { isAuthenticated, loading } = useAuth();

  if (window.location.pathname === '/oauth/callback') {
    return <OAuthCallback />;
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center text-slate-400">
        Carregando sessão...
      </div>
    );
  }

  return isAuthenticated ? <Dashboard /> : <Login />;
}


export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <MainRouter />
      </AuthProvider>
    </ErrorBoundary>
  );
}
