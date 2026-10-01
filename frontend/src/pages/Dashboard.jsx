import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import DemandList from '../components/DemandList';
import NewDemand from './NewDemand';
import DirectorApprovalPanel from '../components/DirectorApprovalPanel';
import GCCPanel from '../components/GCCPanel';
import GCCKanban from '../components/GCCKanban';
import ExecutiveDashboard from '../components/ExecutiveDashboard';
import ExecutiveDeliberationPanel from '../components/ExecutiveDeliberationPanel';
import ComprasModule from '../components/ComprasModule';
import ContratosFluxoModule from '../components/ContratosFluxoModule';
import PlanejamentoEsteiraKanban from '../components/PlanejamentoEsteiraKanban';
import PlanejamentoIndicadoresMinuta from '../components/PlanejamentoIndicadoresMinuta';
import PlanejamentoSentinelaMonitor from '../components/PlanejamentoSentinelaMonitor';
import PlanejamentoCapacidadeWidget from '../components/PlanejamentoCapacidadeWidget';
import GovernancaEsteiraKanban from '../components/GovernancaEsteiraKanban';

export default function Dashboard() {
  const { user, logout } = useAuth();
  const [demands, setDemands] = useState([]);
  const [showNewDemand, setShowNewDemand] = useState(false);
  const [demandToEdit, setDemandToEdit] = useState(null);
  const [loading, setLoading] = useState(true);

  // Controle de expansão/recolhimento da Barra Lateral
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // Macro-Processos na Barra Lateral (1. Planejamento, 2. Contratual, 3. Operacional)
  const [macroFase, setMacroFase] = useState('PLANEJAMENTO');
  const [subTab, setSubTab] = useState('registro');

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
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      {/* Header Topo Global */}
      <header className="bg-slate-800 border-b border-slate-700 px-4 sm:px-6 py-2.5 flex items-center justify-between shadow z-20 shrink-0">
        <div className="flex items-center space-x-3">
          {/* Botão de Alternância da Barra Lateral */}
          <button
            type="button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-slate-750 hover:bg-slate-700 text-slate-200 hover:text-white text-xs font-bold rounded-lg border border-slate-600 transition shadow-sm"
            title={sidebarOpen ? "Recolher Menu Lateral para Expandir Painel" : "Expandir Menu Lateral"}
          >
            <span>{sidebarOpen ? '◀' : '☰'}</span>
            <span className="hidden md:inline">{sidebarOpen ? 'Recolher Menu' : 'Menu Lateral'}</span>
          </button>

          <span className="font-extrabold text-base sm:text-lg text-white tracking-tight flex items-center gap-1.5 sm:gap-2">
            <span>📡</span>
            <span className="bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">TELEBRAS</span>
            <span className="text-slate-500 font-normal">|</span>
            <span className="text-white font-bold">PLAC</span>
          </span>
          <span className="hidden lg:inline bg-blue-600/20 text-blue-300 text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border border-blue-500/30">
            Painel de Planejamento &amp; Governança
          </span>
        </div>

        <div className="flex items-center space-x-3 sm:space-x-4">
          <div className="text-right">
            <p className="text-xs font-bold text-white">{user?.username}</p>
            <p className="text-[10px] text-slate-400">{roleLabels[user?.role] || user?.role}</p>
          </div>
          <button
            onClick={logout}
            className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded transition shadow-sm font-medium"
          >
            Sair
          </button>
        </div>
      </header>

      {/* Corpo: Sidebar Retrátil + Área de Trabalho Expandida */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar Lateral Esquerda (Retrátil) */}
        {sidebarOpen && (
          <aside className="w-64 sm:w-72 bg-slate-950 border-r border-slate-800 flex flex-col justify-between shrink-0 shadow-2xl transition-all duration-300">
            <div className="p-3.5 space-y-3">
              <div className="flex items-center justify-between px-1">
                <div>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                    Macro-Processos
                  </span>
                  <p className="text-[11px] text-slate-400">
                    Selecione a esteira:
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => setSidebarOpen(false)}
                  className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-850 text-xs transition"
                  title="Recolher Menu"
                >
                  ◀
                </button>
              </div>

              <nav className="space-y-2">
                {/* Macro 1: Gestão Estratégica de Planejamento */}
                <button
                  type="button"
                  onClick={() => {
                    setMacroFase('PLANEJAMENTO');
                    setSubTab('registro');
                    setShowNewDemand(false);
                  }}
                  className={`w-full text-left p-3 rounded-xl border transition flex items-start gap-2.5 ${
                    macroFase === 'PLANEJAMENTO'
                      ? 'bg-blue-950/70 border-blue-500 text-white shadow-lg shadow-blue-500/10 ring-1 ring-blue-500/40'
                      : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:bg-slate-850 hover:text-slate-200'
                  }`}
                >
                  <span className="text-xl mt-0.5">📌</span>
                  <div>
                    <div className="text-xs font-extrabold text-white flex items-center gap-1.5">
                      1. Planejamento Estratégico
                    </div>
                    <div className="text-[10px] text-blue-300 font-semibold mt-0.5">
                      Rito PLAC &amp; Previsão 99%
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5 leading-relaxed">
                      Levantamento, Aprovação Diretor, Esteira e Sentinela.
                    </div>
                  </div>
                </button>

                {/* Macro 2: Gestão Contratual & Licitações */}
                <button
                  type="button"
                  onClick={() => {
                    setMacroFase('CONTRATUAL');
                    setSubTab('esteira_gcc');
                    setShowNewDemand(false);
                  }}
                  className={`w-full text-left p-3 rounded-xl border transition flex items-start gap-2.5 ${
                    macroFase === 'CONTRATUAL'
                      ? 'bg-purple-950/70 border-purple-500 text-white shadow-lg shadow-purple-500/10 ring-1 ring-purple-500/40'
                      : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:bg-slate-850 hover:text-slate-200'
                  }`}
                >
                  <span className="text-xl mt-0.5">📑</span>
                  <div>
                    <div className="text-xs font-extrabold text-white flex items-center gap-1.5">
                      2. Gestão Contratual &amp; GCC
                    </div>
                    <div className="text-[10px] text-purple-300 font-semibold mt-0.5">
                      Licitações &amp; Compras
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5 leading-relaxed">
                      Esteira de certames da GCC e deliberação executiva.
                    </div>
                  </div>
                </button>

                {/* Macro 3: Execução & Fiscalização Operacional */}
                <button
                  type="button"
                  onClick={() => {
                    setMacroFase('OPERACIONAL');
                    setSubTab('contratos_vigentes');
                    setShowNewDemand(false);
                  }}
                  className={`w-full text-left p-3 rounded-xl border transition flex items-start gap-2.5 ${
                    macroFase === 'OPERACIONAL'
                      ? 'bg-emerald-950/70 border-emerald-500 text-white shadow-lg shadow-emerald-500/10 ring-1 ring-emerald-500/40'
                      : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:bg-slate-850 hover:text-slate-200'
                  }`}
                >
                  <span className="text-xl mt-0.5">📦</span>
                  <div>
                    <div className="text-xs font-extrabold text-white flex items-center gap-1.5">
                      3. Execução &amp; Fiscalização
                    </div>
                    <div className="text-[10px] text-emerald-300 font-semibold mt-0.5">
                      Contratos Vigentes &amp; Entregas
                    </div>
                    <div className="text-[10px] text-slate-400 mt-0.5 leading-relaxed">
                      Entregas físicas no local, fiscais e medições.
                    </div>
                  </div>
                </button>
              </nav>
            </div>

            {/* Rodapé da Sidebar */}
            <div className="p-3 border-t border-slate-800 bg-slate-950/90">
              <div className="bg-slate-900/90 rounded-xl p-2.5 border border-slate-800 text-[10px] text-slate-400 space-y-0.5 shadow-inner">
                <div className="font-bold text-slate-200 flex items-center gap-1.5">
                  <span>🤖</span> Motor Estatístico Ativo
                </div>
                <p className="leading-tight text-slate-400">
                  IC 99% (Z=2,576) calibrado com dados empíricos reais da Telebras.
                </p>
              </div>
            </div>
          </aside>
        )}

        {/* Painel à Direita: Abas Sequenciais da Macro-Fase + Telas Expandidas */}
        <div className="flex-1 flex flex-col overflow-y-auto w-full transition-all duration-300">
          {/* Barra Superior Dinâmica de Abas Sequenciais */}
          <div className="bg-slate-850 border-b border-slate-700/80 px-4 sm:px-6 shrink-0 sticky top-0 z-10 shadow-sm flex items-center justify-between">
            <div className="flex space-x-1 sm:space-x-2 overflow-x-auto py-0">
              {macroFase === 'PLANEJAMENTO' && (
                <>
                  <button
                    type="button"
                    onClick={() => { setSubTab('registro'); setShowNewDemand(false); fetchDemands(); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'registro'
                        ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📝</span>
                    <span>Fase 1: Registro de Necessidades</span>
                    <span className="text-[10px] text-blue-400/80 font-mono font-normal">(&amp; Certidão)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('validacao'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'validacao'
                        ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>⚖️</span>
                    <span>Fase 2: Validação da Diretoria</span>
                    <span className="text-[10px] text-amber-400/80 font-mono font-normal">(Trava SIGA)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('consolidacao'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'consolidacao'
                        ? 'border-blue-500 text-blue-400 bg-blue-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📋</span>
                    <span>Fase 3: Esteira Kanban Integrada</span>
                    <span className="text-[10px] text-cyan-400 font-mono font-bold bg-cyan-950/60 px-1.5 py-0.5 rounded border border-cyan-500/30">
                      Kanban + SIGA
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('indicadores_minuta'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'indicadores_minuta'
                        ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10 shadow-sm'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📜</span>
                    <span>Fase 4: Indicadores da Minuta PLAC</span>
                    <span className="text-[10px] text-indigo-400 font-mono font-bold bg-indigo-950/60 px-1.5 py-0.5 rounded border border-indigo-500/30">
                      (Art. 47 &amp; Anexo IV)
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('previsoes_capacidade'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'previsoes_capacidade'
                        ? 'border-amber-500 text-amber-400 bg-amber-500/10 shadow-sm'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📊</span>
                    <span>Previsão dos 3 Cenários &amp; Capacidade</span>
                    <span className="text-[10px] text-amber-400 font-mono font-bold bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-500/30">
                      (10 Modalidades)
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('estatistica_pert'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'estatistica_pert'
                        ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10 shadow-sm'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📈</span>
                    <span>Inferência Estatística &amp; PERT</span>
                    <span className="text-[10px] text-emerald-400 font-mono font-bold bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-500/30">
                      n=61 PEs • n=28 DEs
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('sentinela'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'sentinela'
                        ? 'border-purple-500 text-purple-400 bg-purple-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>🤖</span>
                    <span>Sentinela &amp; Governança PLAC</span>
                    <span className="text-[10px] text-purple-400 font-mono font-normal">(IAC/ICNP)</span>
                  </button>
                </>
              )}

              {macroFase === 'CONTRATUAL' && (
                <>
                  <button
                    type="button"
                    onClick={() => { setSubTab('esteira_gcc'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'esteira_gcc'
                        ? 'border-purple-500 text-purple-400 bg-purple-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>🏢</span>
                    <span>Esteira de Licitações GCC</span>
                    <span className="text-[10px] text-purple-400/80 font-mono font-normal">(Kanban Certames)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('previsoes_capacidade'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'previsoes_capacidade'
                        ? 'border-amber-500 text-amber-400 bg-amber-500/10 shadow-sm'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📊</span>
                    <span>Previsão 3 Cenários &amp; Capacidade</span>
                    <span className="text-[10px] text-amber-400 font-mono font-bold bg-amber-950/60 px-1.5 py-0.5 rounded border border-amber-500/30">
                      (10 Modalidades)
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('estatistica_pert'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'estatistica_pert'
                        ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10 shadow-sm'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📈</span>
                    <span>Inferência Estatística &amp; PERT</span>
                    <span className="text-[10px] text-emerald-400 font-mono font-bold bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-500/30">
                      n=61 PEs • n=28 DEs
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('tribunal_ia'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'tribunal_ia'
                        ? 'border-purple-500 text-purple-400 bg-purple-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>⚖️</span>
                    <span>Tribunal de Riscos &amp; Conformidade</span>
                    <span className="text-[10px] text-slate-400 font-mono font-normal">(Jurisprudência TCU)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('deliberacao_redir'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'deliberacao_redir'
                        ? 'border-purple-500 text-purple-400 bg-purple-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>🏛️</span>
                    <span>Deliberação Executiva REDIR</span>
                    <span className="text-[10px] text-slate-400 font-mono font-normal">(UC05)</span>
                  </button>
                </>
              )}

              {macroFase === 'OPERACIONAL' && (
                <>
                  <button
                    type="button"
                    onClick={() => { setSubTab('contratos_vigentes'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'contratos_vigentes'
                        ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📦</span>
                    <span>Contratos Vigentes &amp; Entregas no Local</span>
                    <span className="text-[10px] text-emerald-400/80 font-mono font-normal">(PNCP / Execução)</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => { setSubTab('painel_executivo'); setShowNewDemand(false); }}
                    className={`flex items-center gap-2 py-3 px-3 text-xs font-bold border-b-2 transition whitespace-nowrap ${
                      subTab === 'painel_executivo'
                        ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
                        : 'border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <span>📊</span>
                    <span>Painel Executivo de Indicadores</span>
                    <span className="text-[10px] text-slate-400 font-mono font-normal">(KPIs Globais)</span>
                  </button>
                </>
              )}
            </div>
          </div>

          {/* Conteúdo Renderizado da Sub-fase com Largura Total */}
          <main className="flex-1 p-4 sm:p-6 space-y-6 w-full">
            {/* Telas de Planejamento */}
            {macroFase === 'PLANEJAMENTO' && subTab === 'registro' && (
              showNewDemand ? (
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
              )
            )}

            {macroFase === 'PLANEJAMENTO' && subTab === 'validacao' && (
              <DirectorApprovalPanel />
            )}

            {macroFase === 'PLANEJAMENTO' && subTab === 'consolidacao' && (
              <div className="h-[calc(100vh-140px)] p-4">
                <GovernancaEsteiraKanban />
              </div>
            )}

            {macroFase === 'PLANEJAMENTO' && subTab === 'indicadores_minuta' && (
              <PlanejamentoIndicadoresMinuta />
            )}

            {macroFase === 'PLANEJAMENTO' && subTab === 'previsoes_capacidade' && (
              <PlanejamentoCapacidadeWidget />
            )}

            {macroFase === 'PLANEJAMENTO' && subTab === 'estatistica_pert' && (
              <ContratosFluxoModule initialTab="estatistica" />
            )}

            {macroFase === 'PLANEJAMENTO' && subTab === 'sentinela' && (
              <PlanejamentoSentinelaMonitor />
            )}

            {/* Telas de Gestão Contratual */}
            {macroFase === 'CONTRATUAL' && subTab === 'esteira_gcc' && (
              <GCCKanban />
            )}

            {macroFase === 'CONTRATUAL' && subTab === 'previsoes_capacidade' && (
              <PlanejamentoCapacidadeWidget />
            )}

            {macroFase === 'CONTRATUAL' && subTab === 'estatistica_pert' && (
              <ContratosFluxoModule initialTab="estatistica" />
            )}

            {macroFase === 'CONTRATUAL' && subTab === 'tribunal_ia' && (
              <ComprasModule />
            )}

            {macroFase === 'CONTRATUAL' && subTab === 'deliberacao_redir' && (
              <ExecutiveDeliberationPanel />
            )}

            {/* Telas de Execução & Fiscalização Operacional */}
            {macroFase === 'OPERACIONAL' && subTab === 'contratos_vigentes' && (
              <ContratosFluxoModule initialTab="panorama" />
            )}

            {macroFase === 'OPERACIONAL' && subTab === 'painel_executivo' && (
              <ExecutiveDashboard />
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
