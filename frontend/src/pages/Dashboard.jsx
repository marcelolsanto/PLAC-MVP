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
      <div className="bg-slate-850 border-b border-slate-800 px-6 py-2">
        <div className="max-w-5xl mx-auto flex gap-6 overflow-x-auto">
          <button
            onClick={() => {
              setActiveTab('executive');
              setShowNewDemand(false);
            }}
            className={`text-sm pb-2 font-medium border-b-2 whitespace-nowrap transition ${
              activeTab === 'executive'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            📊 Painel Executivo & KPIs (UC04)
          </button>

          <button
            onClick={() => {
              setActiveTab('demands');
              setShowNewDemand(false);
              fetchDemands();
            }}
            className={`text-sm pb-2 font-medium border-b-2 whitespace-nowrap transition ${
              activeTab === 'demands'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            📝 Registrar Necessidades (UC01)
          </button>

          <button
            onClick={() => {
              setActiveTab('approval');
              setShowNewDemand(false);
            }}
            className={`text-sm pb-2 font-medium border-b-2 whitespace-nowrap transition ${
              activeTab === 'approval'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            ⚖️ Validação do Diretor (UC02)
          </button>

          <button
            onClick={() => {
              setActiveTab('gcc');
              setShowNewDemand(false);
            }}
            className={`text-sm pb-2 font-medium border-b-2 whitespace-nowrap transition ${
              activeTab === 'gcc'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            📅 Consolidação GCC & Calendário (UC03)
          </button>

          <button
            onClick={() => {
              setActiveTab('deliberation');
              setShowNewDemand(false);
            }}
            className={`text-sm pb-2 font-medium border-b-2 whitespace-nowrap transition ${
              activeTab === 'deliberation'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            🏛️ Deliberação REDIR & DAFRI (UC05/UC06)
          </button>
        </div>
      </div>

      {/* Conteúdo Principal */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 space-y-6">
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
