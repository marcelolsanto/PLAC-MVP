import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import DemandList from '../components/DemandList';
import NewDemand from './NewDemand';
import DirectorApprovalPanel from '../components/DirectorApprovalPanel';
import GCCPanel from '../components/GCCPanel';
import ExecutiveDashboard from '../components/ExecutiveDashboard';
import ExecutiveDeliberationPanel from '../components/ExecutiveDeliberationPanel';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [demands, setDemands] = useState([]);
  const [showNewDemand, setShowNewDemand] = useState(false);
  const [demandToEdit, setDemandToEdit] = useState(null);
  const [activeTab, setActiveTab] = useState('executive'); // 'executive', 'demands', 'approval', 'gcc'
  const [loading, setLoading] = useState(true);

  const fetchDemands = async () => {
    try {
      setLoading(true);
      const res = await api.get('/demands/');
      setDemands(res.data);
    } catch (err) {
      console.error('Erro ao buscar demandas', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDemands();
  }, []);

  const roleLabels = {
    DEMANDANTE: 'Representante da Área Demandante',
    DIRETOR: 'Diretor(a) da Área Requisitante',
    ANALISTA_GCC: 'Analista da GCC',
    DIRETOR_DAFRI: 'Diretor(a) da DAFRI',
    DIRETORIA_EXECUTIVA: 'Diretoria Executiva',
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 px-6 py-4 flex items-center justify-between shadow">
        <div className="flex items-center space-x-3">
          <span className="font-bold text-lg text-white">PLAC - Gestão de Contratações</span>
          <span className="bg-blue-600/20 text-blue-400 text-xs px-2.5 py-1 rounded-full border border-blue-500/30">
            MVP Executivo
          </span>
        </div>

        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="text-sm font-medium text-white">{user?.username}</p>
            <p className="text-xs text-slate-400">{roleLabels[user?.role] || user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded transition"
          >
            Sair
          </button>
        </div>
      </header>

      {/* Navegação por Abas para Demonstração de Ponta a Ponta */}
      <div className="bg-slate-850 border-b border-slate-700">
        <div className="flex w-full">
          <button
            onClick={() => {
              setActiveTab('executive');
              setShowNewDemand(false);
            }}
            className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-3 px-2 border-b-2 transition ${
              activeTab === 'executive'
                ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <span>📊</span>
            <span className="hidden sm:inline">Painel Executivo &amp; KPIs</span>
            <span className="sm:hidden">KPIs</span>
            <span className="hidden md:inline text-slate-500 text-[10px]">(UC04)</span>
          </button>

          <button
            onClick={() => {
              setActiveTab('demands');
              setShowNewDemand(false);
              fetchDemands();
            }}
            className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-3 px-2 border-b-2 transition ${
              activeTab === 'demands'
                ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <span>📝</span>
            <span className="hidden sm:inline">Registrar Necessidades</span>
            <span className="sm:hidden">Demandas</span>
            <span className="hidden md:inline text-slate-500 text-[10px]">(UC01)</span>
          </button>

          <button
            onClick={() => {
              setActiveTab('approval');
              setShowNewDemand(false);
            }}
            className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-3 px-2 border-b-2 transition ${
              activeTab === 'approval'
                ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <span>⚖️</span>
            <span className="hidden sm:inline">Validação do Diretor</span>
            <span className="sm:hidden">Diretor</span>
            <span className="hidden md:inline text-slate-500 text-[10px]">(UC02)</span>
          </button>

          <button
            onClick={() => {
              setActiveTab('gcc');
              setShowNewDemand(false);
            }}
            className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-3 px-2 border-b-2 transition ${
              activeTab === 'gcc'
                ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <span>📅</span>
            <span className="hidden sm:inline">Consolidação GCC</span>
            <span className="sm:hidden">GCC</span>
            <span className="hidden md:inline text-slate-500 text-[10px]">(UC03)</span>
          </button>

          <button
            onClick={() => {
              setActiveTab('deliberation');
              setShowNewDemand(false);
            }}
            className={`flex-1 flex items-center justify-center gap-1.5 text-xs font-medium py-3 px-2 border-b-2 transition ${
              activeTab === 'deliberation'
                ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            <span>🏛️</span>
            <span className="hidden sm:inline">Deliberação REDIR &amp; DAFRI</span>
            <span className="sm:hidden">REDIR</span>
            <span className="hidden md:inline text-slate-500 text-[10px]">(UC05/06)</span>
          </button>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <main className="flex-1 w-full mx-auto p-6 space-y-6 max-w-7xl">
        {activeTab === 'executive' ? (
          <ExecutiveDashboard />
        ) : activeTab === 'gcc' ? (
          <GCCPanel />
        ) : activeTab === 'approval' ? (
          <DirectorApprovalPanel />
        ) : activeTab === 'deliberation' ? (
          <ExecutiveDeliberationPanel />
        ) : showNewDemand ? (
          <NewDemand
            demandToEdit={demandToEdit}
            onDemandCreated={() => {
              setDemandToEdit(null);
              setShowNewDemand(false);
              fetchDemands();
            }}
            onCancel={() => {
              setDemandToEdit(null);
              setShowNewDemand(false);
            }}
          />
        ) : (
          <div>
            {loading ? (
              <div className="text-center py-12 text-slate-400">Carregando esteira de demandas...</div>
            ) : (
              <DemandList
                demands={demands}
                onNewDemandClick={() => {
                  setDemandToEdit(null);
                  setShowNewDemand(true);
                }}
                onEditDemandClick={(demand) => {
                  setDemandToEdit(demand);
                  setShowNewDemand(true);
                }}
              />
            )}
          </div>
        )}
      </main>
    </div>
  );
}
