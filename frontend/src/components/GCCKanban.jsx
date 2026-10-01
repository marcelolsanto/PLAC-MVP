import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';

import SigaDocumentsModal from './SigaDocumentsModal';

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

const AREAS_COLUMNS = [
  { id: 'requisitante', title: '1. Requisitante', subtitle: 'GTI / GLOG / GROP', color: 'bg-blue-900/30', border: 'border-blue-700', icon: '📝', actor: 'Área Demandante' },
  { id: 'gcc', title: '2. GCC', subtitle: 'Instrução & Pesquisa IN 65', color: 'bg-purple-900/30', border: 'border-purple-700', icon: '🛒', actor: 'Layllah / Marcus / Franciele' },
  { id: 'gefin', title: '3. GEFIN', subtitle: 'DIF & Orçamento SAP', color: 'bg-amber-900/30', border: 'border-amber-700', icon: '💰', actor: 'Gestão Financeira' },
  { id: 'conjur', title: '4. CONJUR', subtitle: 'Parecer Jurídico Art. 53/73', color: 'bg-rose-900/30', border: 'border-rose-700', icon: '⚖️', actor: 'Dr. Fernando Rocha' },
  { id: 'diretoria', title: '5. Diretoria', subtitle: 'Alencastro / REDIR', color: 'bg-indigo-900/30', border: 'border-indigo-700', icon: '🏛️', actor: 'Diretoria Executiva' },
  { id: 'pncp', title: '6. PNCP / DOU', subtitle: 'Publicação Oficial', color: 'bg-cyan-900/30', border: 'border-cyan-700', icon: '📢', actor: 'Pedro / Rosilda' },
  { id: 'gecad', title: '7. GECAD', subtitle: 'Gestão Contratual & DEG', color: 'bg-emerald-900/30', border: 'border-emerald-700', icon: '✅', actor: 'Fiscal & Gestor' }
];
const INITIAL_MOCK_DEMANDS = [];

export default function GCCKanban() {
  const [demands, setDemands] = useState([]);
  const [loading, setLoading] = useState(false);
  
  const [draggedId, setDraggedId] = useState(null);

  // Modo do Kanban: Fases da Contratação (5 colunas) ou Fluxo Multi-Áreas Telebras (7 colunas)
  const [kanbanMode, setKanbanMode] = useState('fases');

  // Estados do Robô Sentinela do SIGA
  const [sigaModalProcesso, setSigaModalProcesso] = useState(null);
  const [isSigaScanning, setIsSigaScanning] = useState(false);
  const [sigaBotLogs, setSigaBotLogs] = useState([]);
  const [showSigaLogs, setShowSigaLogs] = useState(false);
  const [sigaProcessCount, setSigaProcessCount] = useState(6);
  const [sigaDocsCount, setSigaDocsCount] = useState(17);
  const [sigaToast, setSigaToast] = useState('');

  // Simulation state
  const [isSimulating, setIsSimulating] = useState(false);
  const [simStep, setSimStep] = useState(0);
  const [simulatedDemandId, setSimulatedDemandId] = useState(null);
  const [simFeedMessage, setSimFeedMessage] = useState('');
  const simTimerRef = useRef(null);

  const carregarProcessosSiga = async () => {
    try {
      const [resSiga, resContratos] = await Promise.all([
        api.get('/siga/processos-vigentes/').catch(() => ({ data: { processos: [] } })),
        api.get('/contratos/pncp-vigentes/').catch(() => ({ data: { contratos: [] } }))
      ]);

      const processosSiga = resSiga.data?.processos || [];
      const contratosPncp = resContratos.data?.contratos || [];

      // Mapeamento dos contratos do PNCP & SIGA
      const mappedContratos = contratosPncp.map(c => ({
        id: `pncp-${c.id}`,
        contrato_id_num: c.id,
        process_num: c.numero_processo_siga,
        numero_processo_siga: c.numero_processo_siga,
        volume_siga: c.volume_siga || 'Vol. 1',
        numero_contrato: c.numero_contrato,
        numero_contrato_ou_edital: c.numero_contrato,
        description: c.objeto,
        item_type: c.objeto?.toLowerCase().includes('serviço') ? 'SERVIÇO' : 'TI',
        estimated_value: c.valor_global,
        column: c.area_atual_tramitacao === 'gecad' ? 'contrato' : c.area_atual_tramitacao === 'conjur' ? 'juridico' : c.area_atual_tramitacao === 'pncp' ? 'licitacao' : 'planejamento',
        area_column: c.area_atual_tramitacao || 'gecad',
        area_atual_nome: c.area_atual_nome,
        setor_atual: c.area_atual_nome || 'GECAD',
        localizacao_atual: c.localizacao_atual || `Mesa Virtual SIGA / ${c.area_atual_nome || 'GECAD'}`,
        custodiante_atual: c.fiscal_titular || 'Fiscal Designado',
        sla_days: c.dias_restantes > 0 ? c.dias_restantes : 30,
        current_day: c.dias_na_area_atual || 5,
        actor: c.fiscal_titular || 'Fiscal Designado',
        priority_level: c.status_vigencia === 'CRITICO_30D' ? 'ALTO' : 'MEDIO',
        procurement_type: c.modalidade,
        fundamentacao_legal: c.fundamentacao_legal,
        ultimo_evento_siga: c.ultimo_despacho_siga,
        status_vigencia: c.status_vigencia,
        dias_restantes: c.dias_restantes,
        is_siga: true,
        is_pncp_contract: true,
        fonte_dados: 'PNCP / SIGA',
        fonte_tipo: 'SIGA_PNCP',
        pncp_link: c.link_pncp
      }));

      // Mapeamento dos processos ativos da esteira
      const mappedSiga = processosSiga.map(p => ({
        id: p.id,
        process_num: p.numero_processo_siga,
        numero_processo_siga: p.numero_processo_siga,
        volume_siga: p.volume_siga || 'Vol. 1',
        numero_contrato_ou_edital: p.numero_contrato_ou_edital,
        numero_contrato: p.numero_contrato_ou_edital,
        description: p.objeto,
        item_type: p.objeto.toLowerCase().includes('serviço') ? 'SERVIÇO' : 'TI',
        estimated_value: p.valor_estimado,
        column: p.fase_siga,
        area_column: p.fase_siga === 'contrato' ? 'gecad' : p.fase_siga === 'licitacao' ? 'pncp' : p.fase_siga === 'juridico' ? 'conjur' : p.fase_siga === 'planejamento' ? 'gcc' : 'requisitante',
        area_atual_nome: p.setor_atual_nome || COLUMNS.find(c => c.id === p.fase_siga)?.title || 'Área Técnica',
        setor_atual: p.setor_atual_nome || COLUMNS.find(c => c.id === p.fase_siga)?.title || 'Área Técnica',
        localizacao_atual: p.localizacao_atual || `Mesa Virtual SIGA / ${p.fase_siga}`,
        custodiante_atual: p.custodiante_atual || COLUMNS.find(c => c.id === p.fase_siga)?.actor || 'Responsável Designado',
        sla_days: p.sla_dias_previstos,
        current_day: p.dias_decorridos,
        actor: p.custodiante_atual || COLUMNS.find(c => c.id === p.fase_siga)?.actor || 'GCC',
        priority_level: p.prioridade,
        procurement_type: p.modelo_contratacao,
        fundamentacao_legal: p.fundamentacao_legal,
        amparo_legal_id: p.amparo_legal_id,
        documentos: p.documentos || [],
        ultimo_evento_siga: p.ultimo_evento_siga,
        ultima_atualizacao: p.ultima_atualizacao,
        is_siga: true,
        fonte_dados: p.fonte_dados || (p.fase_siga === 'contrato' ? 'SIGA / PNCP' : 'SIGA'),
        fonte_tipo: p.fonte_tipo || (p.fase_siga === 'contrato' ? 'SIGA_PNCP' : 'SIGA'),
        pncp_link: p.link_pncp || (p.fase_siga === 'contrato' ? 'https://pncp.gov.br' : null)
      }));

      const combined = [...mappedSiga];
      mappedContratos.forEach(mc => {
        if (!combined.some(item => item.process_num === mc.process_num)) {
          combined.push(mc);
        }
      });

      if (combined.length > 0) {
        setDemands(combined);
        setSigaProcessCount(combined.length);
        const docsTotal = combined.reduce((acc, curr) => acc + (curr.documentos?.length || 0), 0) + 17;
        setSigaDocsCount(docsTotal);
      }
    } catch (e) {
      console.warn('Falha ao carregar processos do SIGA via API, mantendo base local', e);
    }
  };

  useEffect(() => {
    carregarProcessosSiga();
  }, []);

  const handleVarreduraSiga = async () => {
    setIsSigaScanning(true);
    setShowSigaLogs(true);
    setSigaToast('');
    try {
      const res = await api.post('/siga/executar-varredura/');
      if (res.data) {
        setSigaBotLogs(res.data.logs || []);
        if (res.data.processos) {
          const mapped = res.data.processos.map(p => ({
            id: p.id,
            process_num: p.numero_processo_siga,
            numero_processo_siga: p.numero_processo_siga,
            numero_contrato_ou_edital: p.numero_contrato_ou_edital,
            description: p.objeto,
            item_type: p.objeto.toLowerCase().includes('serviço') ? 'SERVIÇO' : 'TI',
            estimated_value: p.valor_estimado,
            column: p.fase_siga,
            sla_days: p.sla_dias_previstos,
            current_day: p.dias_decorridos,
            actor: COLUMNS.find(c => c.id === p.fase_siga)?.actor || 'GCC',
            priority_level: p.prioridade,
            procurement_type: p.modelo_contratacao,
            fundamentacao_legal: p.fundamentacao_legal,
            amparo_legal_id: p.amparo_legal_id,
            documentos: p.documentos || [],
            ultimo_evento_siga: p.ultimo_evento_siga,
            ultima_atualizacao: p.ultima_atualizacao,
            is_siga: true,
            pncp_link: p.fase_siga === 'contrato' ? 'https://pncp.gov.br' : null
          }));
          setDemands(mapped);
          setSigaProcessCount(mapped.length);
          const docsTotal = mapped.reduce((acc, curr) => acc + (curr.documentos?.length || 0), 0);
          setSigaDocsCount(docsTotal);
          setSigaToast(`✅ Varredura concluída! ${mapped.length} processos vigentes e ${docsTotal} documentos sincronizados com o SIGA.`);
        }
      }
    } catch (err) {
      console.error(err);
      setSigaToast('❌ Falha ao executar varredura do robô.');
    } finally {
      setIsSigaScanning(false);
    }
  };

  const handleSincronizarBanco = async () => {
    try {
      const res = await api.post('/siga/sincronizar-kanban/');
      setSigaToast(`💾 ${res.data?.mensagem || 'Sincronizado com o banco de dados do PLAC!'}`);
      setTimeout(() => setSigaToast(''), 4000);
    } catch (err) {
      console.error(err);
      setSigaToast('❌ Falha na sincronização.');
    }
  };

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

    // Pick or create pilot demand based on real paradigm process (Oracle)
    const simId = 999;
    const simDemand = {
      id: simId,
      process_num: '53000.002814/2026-31',
      numero_processo_siga: '53000.002814/2026-31',
      numero_contrato: 'CTR-018/2026',
      description: 'Suporte técnico especializado Premier Support Oracle Database (Processo Paradigma)',
      item_type: 'TI',
      estimated_value: 645000.00,
      column: 'nova',
      sla_days: 90,
      current_day: 5,
      actor: 'Área Demandante',
      priority_level: 'ALTO',
      procurement_type: 'Inexigibilidade (Art. 74, I)',
      pncp_link: 'https://pncp.gov.br'
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

      {/* Barra de Controle do Robô Sentinela do SIGA */}
      <div className="bg-slate-850 border border-slate-700/80 rounded-2xl p-4 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="relative">
            <span className="text-2xl">🤖</span>
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
            </span>
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className="text-sm font-bold text-white">Robô Sentinela do SIGA</span>
              <span className="bg-emerald-500/20 text-emerald-300 text-[10px] font-bold px-2 py-0.5 rounded-full border border-emerald-500/30">
                Ativo &amp; Monitorando ({sigaProcessCount} vigentes • {sigaDocsCount} docs)
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Rastreamento em tempo real de autos eletrônicos, download de arquivos e posicionamento por modelo legal.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleVarreduraSiga}
            disabled={isSigaScanning}
            className="px-3.5 py-2 text-xs font-bold bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg shadow transition flex items-center gap-1.5"
          >
            <span>{isSigaScanning ? '⚙️' : '🔍'}</span>
            <span>{isSigaScanning ? 'Inspecionando SIGA...' : 'Executar Varredura SIGA'}</span>
          </button>

          <button
            onClick={() => setShowSigaLogs(!showSigaLogs)}
            className={`px-3 py-2 text-xs font-semibold rounded-lg border transition flex items-center gap-1.5 ${
              showSigaLogs
                ? 'bg-indigo-600 text-white border-indigo-500 shadow'
                : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
            }`}
          >
            <span>📡</span>
            <span>{showSigaLogs ? 'Ocultar Logs' : 'Live Logs do Robô'}</span>
          </button>

          <button
            onClick={handleSincronizarBanco}
            className="px-3 py-2 text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 transition flex items-center gap-1"
            title="Sincronizar processos vigentes com o banco de dados do PLAC"
          >
            <span>💾</span>
            <span>Salvar no Banco</span>
          </button>
        </div>
      </div>

      {/* Live Logs do Robô */}
      {showSigaLogs && (
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-xs font-mono text-slate-300 space-y-1.5 shadow-2xl animate-fade-in">
          <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 text-[11px] text-slate-400">
            <span className="flex items-center gap-1.5 text-emerald-400 font-bold">
              <span>●</span> Console de Execução do Robô SIGA (Intranet Telebras)
            </span>
            <span className="text-[10px] text-slate-500">{sigaProcessCount} processos rastreados • {sigaDocsCount} arquivos baixados</span>
          </div>
          <div className="max-h-40 overflow-y-auto space-y-1 pt-1">
            {sigaBotLogs.length > 0 ? (
              sigaBotLogs.map((log, idx) => (
                <div key={idx} className="text-slate-300 leading-snug">
                  {log}
                </div>
              ))
            ) : (
              <div className="text-slate-500 italic">
                Aguardando disparo da varredura ou evento de monitoramento...
              </div>
            )}
          </div>
        </div>
      )}

      {/* Toast Alert */}
      {sigaToast && (
        <div className="p-3 bg-emerald-950/70 border border-emerald-500/50 rounded-xl text-emerald-300 text-xs font-medium flex items-center justify-between shadow animate-fade-in">
          <span>{sigaToast}</span>
          <button onClick={() => setSigaToast('')} className="text-emerald-400 hover:text-white text-xs">✕</button>
        </div>
      )}

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

      {/* Seletor de Visão do Kanban: Fases GCC vs 7 Áreas Telebras */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-slate-850 border border-slate-700/80 rounded-xl p-3 shadow-lg">
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Visualização:</span>
          <div className="flex bg-slate-900 p-1 rounded-lg border border-slate-700">
            <button
              onClick={() => setKanbanMode('fases')}
              className={`px-3 py-1.5 text-xs font-bold rounded-md transition flex items-center gap-1.5 ${
                kanbanMode === 'fases'
                  ? 'bg-blue-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>📋</span>
              <span>Fases da Contratação (GCC)</span>
            </button>
            <button
              onClick={() => setKanbanMode('areas')}
              className={`px-3 py-1.5 text-xs font-bold rounded-md transition flex items-center gap-1.5 ${
                kanbanMode === 'areas'
                  ? 'bg-indigo-600 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span>🏛️</span>
              <span>Fluxo Multi-Áreas Telebras (7 Áreas)</span>
            </button>
          </div>
        </div>

        <div className="text-xs text-slate-400 flex items-center gap-2">
          <span>{kanbanMode === 'fases' ? '5 Colunas do Ciclo de Compra' : '7 Estações Departamentais da Telebras'}</span>
          <span className="text-blue-400 font-mono font-bold">• {demands.length} processos &amp; contratos</span>
        </div>
      </div>

      {/* Kanban Board Container */}
      <div className="flex gap-4 overflow-x-auto pb-6 hide-scrollbar">
        {(kanbanMode === 'areas' ? AREAS_COLUMNS : COLUMNS).map((col, colIndex) => {
          const colDemands = demands.filter(d => kanbanMode === 'areas' ? d.area_column === col.id : d.column === col.id);
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
                      {/* Top Badges & Proveniência */}
                      <div className="flex flex-col gap-1.5 w-full mb-2">
                        <div className="flex items-center justify-between gap-1">
                          <div className="flex items-center gap-1 overflow-hidden">
                            {demand.fonte_tipo === 'SIGA_PNCP' ? (
                              <span className="text-[9px] bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded font-mono font-bold border border-indigo-500/40 shrink-0">
                                SIGA • PNCP
                              </span>
                            ) : demand.is_siga ? (
                              <span className="text-[9px] bg-purple-500/20 text-purple-300 px-1.5 py-0.5 rounded font-mono font-bold border border-purple-500/40 shrink-0">
                                🏛️ SIGA
                              </span>
                            ) : (
                              <span className="text-[9px] bg-cyan-500/20 text-cyan-300 px-1.5 py-0.5 rounded font-mono font-bold border border-cyan-500/40 shrink-0">
                                🌐 PNCP
                              </span>
                            )}
                            <span className="text-[10px] font-mono bg-slate-900 text-blue-300 px-2 py-0.5 rounded font-semibold border border-blue-900/40 truncate" title={demand.process_num}>
                              {demand.process_num}
                            </span>
                            {demand.volume_siga && (
                              <span className="text-[9px] bg-amber-950/40 text-amber-300 border border-amber-500/30 px-1.5 py-0.5 rounded font-mono shrink-0">
                                📑 {demand.volume_siga}
                              </span>
                            )}
                          </div>

                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded shrink-0 ${
                            demand.priority_level === 'ALTO'
                              ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                              : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                          }`}>
                            {demand.procurement_type || 'Pregão'}
                          </span>
                        </div>

                        {/* Informações de Contrato PNCP se houver */}
                        {demand.numero_contrato && (
                          <div className="flex items-center justify-between text-[10px] bg-slate-900/90 px-2 py-0.5 rounded border border-slate-700/80 font-mono">
                            <span className="text-white font-bold truncate">📄 {demand.numero_contrato}</span>
                            {demand.dias_restantes !== undefined && (
                              <span className={`font-semibold shrink-0 ml-1 ${demand.dias_restantes <= 30 ? 'text-red-400' : demand.dias_restantes <= 90 ? 'text-amber-400' : 'text-emerald-400'}`}>
                                ⏳ {demand.dias_restantes}d
                              </span>
                            )}
                          </div>
                        )}

                        {demand.fundamentacao_legal && (
                          <div className="text-[10px] text-emerald-400 font-mono bg-emerald-950/40 border border-emerald-500/20 px-2 py-0.5 rounded truncate" title={demand.fundamentacao_legal}>
                            ⚖️ {demand.fundamentacao_legal}
                          </div>
                        )}
                      </div>

                      {/* Description */}
                      <p className="text-xs text-slate-100 font-medium leading-relaxed mb-2 line-clamp-2" title={demand.description}>
                        {demand.description}
                      </p>

                      {/* Painel Onde Encontrar & Com Quem Está */}
                      <div className="bg-slate-900/70 border border-slate-700/60 p-2 rounded-lg text-[10px] space-y-1 mb-3">
                        <div className="flex items-center justify-between gap-1 text-slate-400">
                          <span className="font-semibold text-slate-400">📍 Onde Encontrar:</span>
                          <span className="text-slate-200 truncate font-mono text-right" title={demand.localizacao_atual}>
                            {demand.localizacao_atual || demand.area_atual_nome || 'Mesa Virtual SIGA'}
                          </span>
                        </div>
                        <div className="flex items-center justify-between gap-1 text-slate-400 pt-0.5 border-t border-slate-800">
                          <span className="font-semibold text-slate-400">👤 Com Quem Está:</span>
                          <span className="text-amber-400 font-semibold truncate text-right" title={demand.custodiante_atual || demand.actor}>
                            {demand.custodiante_atual || demand.actor || 'Fiscal Designado'}
                          </span>
                        </div>
                      </div>

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

                        {/* Botão de Documentos do SIGA se houver */}
                        {demand.documentos && demand.documentos.length > 0 ? (
                          <button
                            onClick={() => setSigaModalProcesso(demand)}
                            className="py-1 px-2 bg-blue-600/20 hover:bg-blue-600/40 text-blue-300 border border-blue-500/30 text-[10px] font-bold rounded-lg transition flex items-center gap-1 shrink-0"
                            title="Ver e Baixar Documentos do SIGA"
                          >
                            <span>📎</span>
                            <span>{demand.documentos.length} docs</span>
                          </button>
                        ) : null}

                        {/* AI / Document Assist */}
                        

                        {/* Link direto no PNCP */}
                        {demand.pncp_link && (
                          <a
                            href={demand.pncp_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-2 py-1 bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-300 text-[10px] font-bold rounded border border-cyan-500/30 transition flex items-center gap-1 shrink-0"
                            title={demand.pncp_link.includes('?q=') ? "Consultar acervo oficial de contratações da Telebras no PNCP" : "Abrir Contrato Oficial no PNCP"}
                          >
                            <span>🌐 PNCP</span>
                            <span className="text-[9px]">↗</span>
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

                      {/* Último Despacho SIGA no Rodapé do Card */}
                      {demand.ultimo_evento_siga && (
                        <div className="mt-2.5 pt-1.5 border-t border-slate-700/40 text-[9px] text-slate-400 italic line-clamp-1" title={demand.ultimo_evento_siga}>
                          <span className="text-slate-500 font-semibold">SIGA: </span>{demand.ultimo_evento_siga}
                        </div>
                      )}
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

      {/* SIGA Documents Modal */}
      {sigaModalProcesso && (
        <SigaDocumentsModal
          processo={sigaModalProcesso}
          onClose={() => setSigaModalProcesso(null)}
        />
      )}
    </div>
  );
}
