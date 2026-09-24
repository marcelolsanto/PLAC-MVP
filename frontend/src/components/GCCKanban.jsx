import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import AIDraftingModal from './AIDraftingModal';

const COLUMNS = [
  { 
    id: 'nova', 
    title: '1. Novas Demandas', 
    subtitle: 'Entrada & Validação', 
    color: 'bg-slate-700/40', 
    border: 'border-slate-600', 
    icon: '📥',
    actor: 'Área Demandante'
  },
  { 
    id: 'planejamento', 
    title: '2. Planejamento', 
    subtitle: 'ETP & Minuta de TR', 
    color: 'bg-blue-900/30', 
    border: 'border-blue-700', 
    icon: '📝',
    actor: 'GCC / Planejamento'
  },
  { 
    id: 'juridico', 
    title: '3. Análise Jurídica', 
    subtitle: 'Parecer Conjur / Art. 53', 
    color: 'bg-purple-900/30', 
    border: 'border-purple-700', 
    icon: '⚖️',
    actor: 'Assessoria Jurídica'
  },
  { 
    id: 'licitacao', 
    title: '4. Licitação / PNCP', 
    subtitle: 'Edital & Disputa', 
    color: 'bg-amber-900/30', 
    border: 'border-amber-700', 
    icon: '📢',
    actor: 'Pregoeiro / CPL'
  },
  { 
    id: 'contrato', 
    title: '5. Homologação & Contrato', 
    subtitle: 'Adjudicação & Assinatura', 
    color: 'bg-emerald-900/30', 
    border: 'border-emerald-700', 
    icon: '✅',
    actor: 'Fiscal & Gestor Contratual'
  },
];

const INITIAL_MOCK_DEMANDS = [
  {
    id: 101,
    process_num: 'TLB-PRO-2026/00280',
    description: 'Manutenções Preventivas e Corretivas nas Antenas do Projeto SGDC',
    item_type: 'SERVIÇO',
    estimated_value: 9396172.94,
    column: 'contrato',
    sla_days: 157,
    current_day: 142,
    actor: 'Fiscal & Gestor Contratual',
    priority_level: 'ALTO',
    procurement_type: 'PE 90010/2026',
    pncp_link: 'https://pncp.gov.br/app/editais/37753638000103/2026/000045'
  },
  {
    id: 102,
    process_num: 'TLB-PRO-2026/02400',
    description: 'Contratação de Seguro Contra Danos e Perdas para o Satélite SGDC-1',
    item_type: 'SERVIÇO',
    estimated_value: 17232657.59,
    column: 'licitacao',
    sla_days: 180,
    current_day: 95,
    actor: 'Pregoeiro / CPL',
    priority_level: 'ALTO',
    procurement_type: 'PE 90012/2026',
    pncp_link: 'https://pncp.gov.br/app/editais/37753638000103/2026/000048'
  },
  {
    id: 103,
    process_num: 'TLB-PRO-2025/07112',
    description: 'Aquisição de Licenças de Software e Suporte Técnico Especializado',
    item_type: 'TI',
    estimated_value: 125000.00,
    column: 'contrato',
    sla_days: 60,
    current_day: 48,
    actor: 'Fiscal & Gestor Contratual',
    priority_level: 'MEDIO',
    procurement_type: 'Dispensa 31/2026',
    pncp_link: 'https://pncp.gov.br/app/editais/37753638000103/2026/000064'
  },
  {
    id: 104,
    process_num: 'TLB-PRO-2025/04501',
    description: 'Contratação de Aplicação Sistêmica de Captura de Documentos Fiscais',
    item_type: 'TI',
    estimated_value: 480000.00,
    column: 'licitacao',
    sla_days: 120,
    current_day: 80,
    actor: 'Pregoeiro / CPL',
    priority_level: 'MEDIO',
    procurement_type: 'PE 32/2026',
    pncp_link: null
  },
  {
    id: 105,
    process_num: 'TLB-PRO-2025/03498',
    description: 'Extensão de Rede de Energia Elétrica para Pontos Operacionais de Telecom',
    item_type: 'OBRA/ENG',
    estimated_value: 1450000.00,
    column: 'juridico',
    sla_days: 157,
    current_day: 62,
    actor: 'Assessoria Jurídica',
    priority_level: 'ALTO',
    procurement_type: 'PE SRP 30/2026',
    pncp_link: null
  },
  {
    id: 106,
    process_num: 'TLB-PRO-2026/00449',
    description: 'Seguro de Responsabilidade Civil para Administradores (D&O 2026/2027)',
    item_type: 'SERVIÇO',
    estimated_value: 390000.00,
    column: 'juridico',
    sla_days: 90,
    current_day: 55,
    actor: 'Assessoria Jurídica',
    priority_level: 'MEDIO',
    procurement_type: 'PE 33/2026',
    pncp_link: null
  },
  {
    id: 107,
    process_num: 'TLB-PRO-2026/01503',
    description: 'Aquisição de Roteadores de Borda e Switches Core de Alta Disponibilidade',
    item_type: 'TI',
    estimated_value: 820000.00,
    column: 'planejamento',
    sla_days: 120,
    current_day: 28,
    actor: 'GCC / Planejamento',
    priority_level: 'ALTO',
    procurement_type: 'PE 90015/2026',
    pncp_link: null
  },
  {
    id: 108,
    process_num: 'TLB-PRO-2026/02741',
    description: 'Renovação do Plano de Saúde e Assistência Odontológica dos Colaboradores',
    item_type: 'SERVIÇO',
    estimated_value: 6200000.00,
    column: 'planejamento',
    sla_days: 180,
    current_day: 35,
    actor: 'GCC / Planejamento',
    priority_level: 'ALTO',
    procurement_type: 'PE 90016/2026',
    pncp_link: null
  },
  {
    id: 109,
    process_num: 'TLB-PRO-2026/03120',
    description: 'Serviço de Recepção, Portaria e Controle de Acesso para a Sede',
    item_type: 'SERVIÇO',
    estimated_value: 1393993.90,
    column: 'nova',
    sla_days: 120,
    current_day: 12,
    actor: 'Área Demandante',
    priority_level: 'MEDIO',
    procurement_type: 'Aguardando GCC',
    pncp_link: null
  },
  {
    id: 110,
    process_num: 'TLB-PRO-2026/03450',
    description: 'Contratação de Plataforma SaaS para Gestão de Vulnerabilidades Cibernéticas',
    item_type: 'TI',
    estimated_value: 310000.00,
    column: 'nova',
    sla_days: 90,
    current_day: 5,
    actor: 'Área Demandante',
    priority_level: 'ALTO',
    procurement_type: 'Aguardando GCC',
    pncp_link: null
  }
];

export default function GCCKanban() {
  const [demands, setDemands] = useState(INITIAL_MOCK_DEMANDS);
  const [loading, setLoading] = useState(false);
  const [aiModalDemand, setAiModalDemand] = useState(null);
  const [draggedId, setDraggedId] = useState(null);

  // Simulation state
  const [isSimulating, setIsSimulating] = useState(false);
  const [simStep, setSimStep] = useState(0);
  const [simulatedDemandId, setSimulatedDemandId] = useState(null);
  const [simFeedMessage, setSimFeedMessage] = useState('');
  const simTimerRef = useRef(null);

  useEffect(() => {
    // Attempt to merge with real backend demands if available
    api.get('/demands/')
      .then(res => {
        if (res.data && res.data.length > 0) {
          const apiDemands = res.data.map((d, idx) => ({
            id: d.id,
            process_num: `TLB-PRO-2026/${String(d.id).padStart(5, '0')}`,
            description: d.description,
            item_type: d.item_type || 'BEM',
            estimated_value: Number(d.estimated_value) || 100000,
            column: COLUMNS[idx % COLUMNS.length].id,
            sla_days: 157,
            current_day: (idx * 25) % 150 + 10,
            actor: COLUMNS[idx % COLUMNS.length].actor,
            priority_level: d.priority_level || 'MEDIO',
            procurement_type: `PE 900${String(d.id).padStart(2, '0')}/2026`,
            pncp_link: d.pncp_published ? 'https://pncp.gov.br' : null
          }));
          // Combine mock realism with real backend records
          setDemands([...INITIAL_MOCK_DEMANDS, ...apiDemands]);
        }
      })
      .catch(err => {
        console.warn('Backend demands fetch fallback to mock', err);
      });
  }, []);

  // Drag and Drop handlers
  const handleDragStart = (e, id) => {
    setDraggedId(id);
    e.dataTransfer.setData('text/plain', String(id));
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e, targetColumnId) => {
    e.preventDefault();
    if (!draggedId) return;

    moveDemandToColumn(draggedId, targetColumnId);
    setDraggedId(null);
  };

  const moveDemandToColumn = (demandId, targetColId) => {
    const targetCol = COLUMNS.find(c => c.id === targetColId);
    setDemands(prev =>
      prev.map(d => {
        if (d.id === demandId) {
          return {
            ...d,
            column: targetColId,
            actor: targetCol ? targetCol.actor : d.actor
          };
        }
        return d;
      })
    );
  };

  // Step advancement buttons
  const stepAdvance = (demandId, direction) => {
    setDemands(prev =>
      prev.map(d => {
        if (d.id === demandId) {
          const currentIndex = COLUMNS.findIndex(c => c.id === d.column);
          const nextIndex = currentIndex + direction;
          if (nextIndex >= 0 && nextIndex < COLUMNS.length) {
            const nextCol = COLUMNS[nextIndex];
            return {
              ...d,
              column: nextCol.id,
              actor: nextCol.actor
            };
          }
        }
        return d;
      })
    );
  };

  // Full-Cycle Automated Simulation
  const startFullCycleSimulation = () => {
    if (isSimulating) {
      // Pause
      clearInterval(simTimerRef.current);
      setIsSimulating(false);
      setSimFeedMessage('⏸️ Simulação pausada pelo usuário.');
      return;
    }

    // Pick or create a pilot demand
    const simId = 999;
    const simDemand = {
      id: simId,
      process_num: 'TLB-SIM-2026/00099',
      description: 'Aquisição de Solução SD-WAN e Segurança de Borda (Piloto Simulado)',
      item_type: 'TI',
      estimated_value: 1850000.00,
      column: 'nova',
      sla_days: 120,
      current_day: 5,
      actor: 'Área Demandante',
      priority_level: 'ALTO',
      procurement_type: 'PE 90038/2026 (Simulação)',
      pncp_link: null
    };

    // Reset board with the sim demand at column 0
    setDemands(prev => [simDemand, ...prev.filter(d => d.id !== simId)]);
    setSimulatedDemandId(simId);
    setIsSimulating(true);

    const stages = [
      {
        col: 'nova',
        msg: '🚀 [ETAPA 1: ENTRADA] Demanda registrada pela Gerência e validada pela Diretoria no PLAC 2026.',
        actor: 'Área Demandante'
      },
      {
        col: 'planejamento',
        msg: '📝 [ETAPA 2: PLANEJAMENTO] A GCC assumiu a demanda. ETP e Termo de Referência gerados com apoio do Copilot IA.',
        actor: 'GCC / Planejamento'
      },
      {
        col: 'juridico',
        msg: '⚖️ [ETAPA 3: JURÍDICO] Minuta remetida à Conjur. Parecer emitido aprovando edital conforme Lei 14.133/2021.',
        actor: 'Assessoria Jurídica'
      },
      {
        col: 'licitacao',
        msg: '📢 [ETAPA 4: LICITAÇÃO & PNCP] Pregão Eletrônico publicado no PNCP e Compras.gov.br. Sessão de disputa de lances concluída!',
        actor: 'Pregoeiro / CPL'
      },
      {
        col: 'contrato',
        msg: '✅ [ETAPA 5: HOMOLOGAÇÃO] Resultado homologado pela autoridade competente e contrato celebrado com sucesso!',
        actor: 'Fiscal & Gestor Contratual'
      }
    ];

    let currentStageIndex = 0;
    setSimFeedMessage(stages[0].msg);

    simTimerRef.current = setInterval(() => {
      currentStageIndex++;
      if (currentStageIndex < stages.length) {
        const stage = stages[currentStageIndex];
        setSimFeedMessage(stage.msg);
        setDemands(prev =>
          prev.map(d => {
            if (d.id === simId) {
              return {
                ...d,
                column: stage.col,
                actor: stage.actor,
                current_day: 15 + currentStageIndex * 25,
                pncp_link: currentStageIndex >= 3 ? 'https://pncp.gov.br' : null
              };
            }
            return d;
          })
        );
      } else {
        clearInterval(simTimerRef.current);
        setIsSimulating(false);
        setSimFeedMessage('🎉 [CICLO COMPLETO CONCLUÍDO] A demanda TLB-SIM-2026/00099 percorreu todo o ciclo de compras com sucesso!');
      }
    }, 2800);
  };

  const resetScenarios = () => {
    if (simTimerRef.current) clearInterval(simTimerRef.current);
    setIsSimulating(false);
    setSimulatedDemandId(null);
    setSimFeedMessage('');
    setDemands(INITIAL_MOCK_DEMANDS);
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Simulation Controls */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-slate-900/60 p-4 border border-slate-800 rounded-2xl backdrop-blur">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              📊 Kanban de Gestão Operacional da GCC
            </h3>
            <span className="text-[10px] bg-blue-500/20 text-blue-400 font-bold px-2 py-0.5 rounded-full border border-blue-500/30">
              Ciclo Completo
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Mapeamento da esteira ponta a ponta: do levantamento da necessidade até a publicação e formalização contratual.
          </p>
        </div>

        {/* Simulation Action Bar */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={startFullCycleSimulation}
            className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-lg shadow-lg transition duration-200 ${
              isSimulating
                ? 'bg-amber-600 hover:bg-amber-700 text-white animate-pulse'
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white'
            }`}
          >
            <span>{isSimulating ? '⏸️ Pausar Simulação' : '▶️ Simular Ciclo Completo'}</span>
          </button>

          <button
            onClick={resetScenarios}
            className="px-3.5 py-2 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition"
          >
            🔄 Resetar Cenários
          </button>
        </div>
      </div>

      {/* Live Simulation Feed Banner */}
      {simFeedMessage && (
        <div className="p-3.5 bg-blue-950/40 border border-blue-500/40 rounded-xl text-blue-300 text-xs flex items-center justify-between shadow-inner animate-fadeIn">
          <div className="flex items-center gap-2.5">
            <span className="text-base animate-spin">{isSimulating ? '⚙️' : '📌'}</span>
            <span className="font-medium">{simFeedMessage}</span>
          </div>
          {isSimulating && (
            <span className="text-[10px] bg-blue-500/20 text-blue-300 px-2 py-0.5 rounded font-mono uppercase tracking-wider">
              Em Execução...
            </span>
          )}
        </div>
      )}

      {/* Kanban Board Container */}
      <div className="flex gap-4 overflow-x-auto pb-6 hide-scrollbar">
        {COLUMNS.map((col, colIndex) => {
          const colDemands = demands.filter(d => d.column === col.id);
          const totalValue = colDemands.reduce((acc, curr) => acc + (curr.estimated_value || 0), 0);

          return (
            <div
              key={col.id}
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, col.id)}
              className="flex-none w-80 flex flex-col h-[calc(100vh-230px)] min-h-[580px]"
            >
              {/* Column Header */}
              <div className={`p-3.5 rounded-t-xl border-t border-x ${col.border} ${col.color} flex flex-col gap-1.5 shadow-sm`}>
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                    <span className="text-lg">{col.icon}</span>
                    <span>{col.title}</span>
                  </h4>
                  <span className="text-xs font-bold text-slate-200 bg-slate-900/70 border border-slate-700/60 px-2.5 py-0.5 rounded-full">
                    {colDemands.length}
                  </span>
                </div>
                
                <div className="flex items-center justify-between text-[11px] text-slate-400">
                  <span className="font-medium text-slate-400">{col.subtitle}</span>
                  <span className="font-mono text-[10px] text-slate-300">
                    R$ {totalValue > 0 ? (totalValue / 1000000).toFixed(1) + 'M' : '0'}
                  </span>
                </div>

                <div className="text-[10px] text-slate-400 bg-slate-900/40 px-2 py-0.5 rounded border border-slate-700/30 flex items-center justify-between">
                  <span>Responsável:</span>
                  <strong className="text-slate-200">{col.actor}</strong>
                </div>
              </div>

              {/* Column Cards Dropzone */}
              <div className={`flex-1 p-2.5 bg-slate-900/30 border-x border-b rounded-b-xl ${col.border} overflow-y-auto space-y-3.5 transition-colors`}>
                {colDemands.map(demand => {
                  const isBeingSimulated = simulatedDemandId === demand.id;

                  return (
                    <div
                      key={demand.id}
                      draggable
                      onDragStart={(e) => handleDragStart(e, demand.id)}
                      className={`p-3.5 bg-slate-800 border rounded-xl shadow-md transition-all duration-200 cursor-grab active:cursor-grabbing group relative ${
                        isBeingSimulated
                          ? 'border-blue-400 ring-2 ring-blue-500/50 shadow-blue-500/20 scale-[1.02] bg-slate-800/90'
                          : 'border-slate-700/80 hover:border-slate-500 hover:shadow-lg'
                      }`}
                    >
                      {/* Top Badges */}
                      <div className="flex items-start justify-between gap-2 mb-2">
                        <span className="text-[10px] font-mono bg-slate-900 text-blue-300 px-2 py-0.5 rounded font-semibold border border-blue-900/40">
                          {demand.process_num}
                        </span>

                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          demand.priority_level === 'ALTO'
                            ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                            : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                        }`}>
                          {demand.procurement_type || 'Pregão'}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-xs text-slate-100 font-medium leading-relaxed mb-3 line-clamp-2" title={demand.description}>
                        {demand.description}
                      </p>

                      {/* Financial & SLA Metrics */}
                      <div className="flex items-center justify-between text-[11px] mb-3 pt-2 border-t border-slate-700/50">
                        <div className="font-semibold text-slate-200 font-mono">
                          R$ {Number(demand.estimated_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </div>

                        <div className="text-[10px] text-slate-400 flex items-center gap-1 font-mono">
                          <span>⏱️</span>
                          <span className={demand.current_day > demand.sla_days ? 'text-red-400 font-bold' : 'text-slate-300'}>
                            {demand.current_day}d / {demand.sla_days}d
                          </span>
                        </div>
                      </div>

                      {/* Virtual Stage Progress Bar */}
                      <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mb-3">
                        <div
                          className={`h-full transition-all duration-500 ${
                            col.id === 'nova'
                              ? 'w-1/5 bg-slate-500'
                              : col.id === 'planejamento'
                              ? 'w-2/5 bg-blue-500'
                              : col.id === 'juridico'
                              ? 'w-3/5 bg-purple-500'
                              : col.id === 'licitacao'
                              ? 'w-4/5 bg-amber-500'
                              : 'w-full bg-emerald-500'
                          }`}
                        ></div>
                      </div>

                      {/* Card Action Footer */}
                      <div className="flex items-center justify-between gap-1.5 pt-1">
                        {/* Step Back button */}
                        <button
                          disabled={colIndex === 0}
                          onClick={() => stepAdvance(demand.id, -1)}
                          title="Voltar Etapa Anterior"
                          className="px-2 py-1 bg-slate-900 hover:bg-slate-700 disabled:opacity-30 disabled:hover:bg-slate-900 text-slate-300 text-xs rounded transition"
                        >
                          ◀
                        </button>

                        {/* AI / Document Assist */}
                        <button
                          onClick={() => setAiModalDemand(demand)}
                          className="flex-1 py-1 px-2 bg-indigo-600/15 hover:bg-indigo-600/30 text-indigo-300 border border-indigo-500/25 text-[10px] font-bold rounded-lg transition text-center flex items-center justify-center gap-1"
                        >
                          <span>✨</span>
                          <span>Copilot IA</span>
                        </button>

                        {/* PNCP link if exists */}
                        {demand.pncp_link && (
                          <a
                            href={demand.pncp_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2 py-1 bg-emerald-500/20 hover:bg-emerald-500/40 text-emerald-300 text-[10px] font-bold rounded border border-emerald-500/30 transition flex items-center gap-0.5"
                            title="Ver Publicação no PNCP"
                          >
                            <span>🌐</span>
                          </a>
                        )}

                        {/* Step Forward button */}
                        <button
                          disabled={colIndex === COLUMNS.length - 1}
                          onClick={() => stepAdvance(demand.id, 1)}
                          title="Avançar para Próxima Etapa"
                          className="px-2 py-1 bg-slate-900 hover:bg-slate-700 disabled:opacity-30 disabled:hover:bg-slate-900 text-slate-300 text-xs rounded transition font-bold text-blue-400"
                        >
                          ▶
                        </button>
                      </div>
                    </div>
                  );
                })}

                {colDemands.length === 0 && (
                  <div className="text-center p-6 text-xs text-slate-500 border border-dashed border-slate-700/60 rounded-xl my-4">
                    Nenhum processo nesta fase
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* AI Drafting Modal */}
      {aiModalDemand && (
        <AIDraftingModal
          demand={aiModalDemand}
          onClose={() => setAiModalDemand(null)}
        />
      )}
    </div>
  );
}
