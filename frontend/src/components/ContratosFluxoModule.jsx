import React, { useState, useEffect } from 'react';
import api from '../services/api';
import SigaDocumentsModal from './SigaDocumentsModal';
import PlanejamentoCapacidadeWidget from './PlanejamentoCapacidadeWidget';
import GovernancaEsteiraKanban from './GovernancaEsteiraKanban';
import PlanejamentoSentinelaMonitor from './PlanejamentoSentinelaMonitor';

export default function ContratosFluxoModule({ initialTab = 'panorama' }) {
  const [activeSubTab, setActiveSubTab] = useState(initialTab); // 'panorama', 'kanban_areas', 'tempo_medio', 'paradigma', 'estatistica', 'capacidade_planejamento'
  const [contratos, setContratos] = useState([]);
  const [resumoAreas, setResumoAreas] = useState(null);
  const [metricasTempo, setMetricasTempo] = useState(null);
  const [paradigma, setParadigma] = useState(null);
  const [kanbanAreas, setKanbanAreas] = useState([]);
  const [dadosEstatisticos, setDadosEstatisticos] = useState(null);
  const [loading, setLoading] = useState(true);

  // Simulador de Previsão Probabilística PERT
  const [simTipo, setSimTipo] = useState('pregao');
  const [simEtapa, setSimEtapa] = useState(1);
  const [simConfianca, setSimConfianca] = useState(80);
  const [simResultado, setSimResultado] = useState(null);
  const [loadingSim, setLoadingSim] = useState(false);

  // Filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [filtroArea, setFiltroArea] = useState('');
  const [filtroVigencia, setFiltroVigencia] = useState('');
  const [filtroModalidade, setFiltroModalidade] = useState('');

  // Modal / Drawer de Inferência IA
  const [inferenciaSelecionada, setInferenciaSelecionada] = useState(null);
  const [loadingInferencia, setLoadingInferencia] = useState(false);
  const [showInferenciaModal, setShowInferenciaModal] = useState(false);

  // Modal de Documentos SIGA
  const [processoDocumentosModal, setProcessoDocumentosModal] = useState(null);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const [resContratos, resAreas, resTempo, resParadigma, resKanban, resStats] = await Promise.all([
        api.get('/contratos/pncp-vigentes/'),
        api.get('/contratos/fluxo-areas-telebras/'),
        api.get('/contratos/tempo-medio-areas/'),
        api.get('/contratos/processo-paradigma/'),
        api.get('/contratos/kanban-areas/'),
        api.get('/estatisticas/inferencia-fluxos/')
      ]);

      setContratos(resContratos.data.contratos || []);
      setResumoAreas(resAreas.data);
      setMetricasTempo(resTempo.data);
      setParadigma(resParadigma.data);
      setKanbanAreas(resKanban.data || []);
      setDadosEstatisticos(resStats.data);
    } catch (err) {
      console.error('Erro ao carregar dados de contratos e fluxo:', err);
    } finally {
      setLoading(false);
    }
  };

  const executarSimulacao = async (tipo, etapa, confianca) => {
    try {
      setLoadingSim(true);
      const res = await api.get(`/estatisticas/previsao/?tipo=${tipo}&etapa=${etapa}&confianca=${confianca}`);
      setSimResultado(res.data);
    } catch (err) {
      console.error('Erro ao calcular previsão probabilística:', err);
    } finally {
      setLoadingSim(false);
    }
  };

  useEffect(() => {
    carregarDados();
  }, []);

  useEffect(() => {
    if (initialTab) {
      setActiveSubTab(initialTab);
    }
  }, [initialTab]);

  useEffect(() => {
    executarSimulacao(simTipo, simEtapa, simConfianca);
  }, [simTipo, simEtapa, simConfianca]);

  const abrirInferenciaIA = async (contratoId) => {
    try {
      setLoadingInferencia(true);
      setShowInferenciaModal(true);
      const res = await api.get(`/contratos/${contratoId}/inferir-tramitacao/`);
      setInferenciaSelecionada(res.data);
    } catch (err) {
      console.error('Erro ao calcular inferência de IA:', err);
    } finally {
      setLoadingInferencia(false);
    }
  };

  const contratosFiltrados = contratos.filter((c) => {
    const matchSearch =
      searchTerm === '' ||
      c.numero_contrato?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.numero_processo_siga?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.fornecedor?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.objeto?.toLowerCase().includes(searchTerm.toLowerCase());

    const matchArea = filtroArea === '' || c.area_atual_tramitacao === filtroArea;
    const matchVigencia = filtroVigencia === '' || c.status_vigencia === filtroVigencia;
    const matchModalidade =
      filtroModalidade === '' || c.modalidade?.toLowerCase().includes(filtroModalidade.toLowerCase());

    return matchSearch && matchArea && matchVigencia && matchModalidade;
  });

  const getCorVigenciaBadge = (status) => {
    switch (status) {
      case 'CRITICO_30D':
        return 'bg-red-500/20 text-red-300 border-red-500/40 animate-pulse';
      case 'ALERTA_90D':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'ATENCAO_180D':
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'REGULAR':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      default:
        return 'bg-slate-700 text-slate-300 border-slate-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Cabeçalho do Módulo */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl pointer-events-none" />
        <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div>
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-blue-600/20 border border-blue-500/30 rounded-xl text-2xl">
                📡
              </div>
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  Contratos Vigentes PNCP &amp; Tramitação SIGA
                  <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs px-2.5 py-0.5 rounded-full">
                    Sincronizado
                  </span>
                </h1>
                <p className="text-sm text-slate-400">
                  Rastreamento do ciclo de vigência dos contratos no PNCP, histórico de tramitação no SIGA e motor de inferência preditiva pelas áreas da Telebras.
                </p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={carregarDados}
              className="bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-medium px-3.5 py-2 rounded-lg border border-slate-600 transition flex items-center gap-2"
            >
              <span>🔄</span> Atualizar Dados
            </button>
          </div>
        </div>

        {/* Métricas Globais (Cards) */}
        {resumoAreas && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
            <div className="bg-slate-900/60 border border-slate-700/80 rounded-lg p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider">Contratos Vigentes (PNCP)</span>
              <div className="text-2xl font-black text-white mt-1">
                {resumoAreas.total_contratos_vigentes}
              </div>
              <span className="text-[11px] text-emerald-400 font-medium">UASG 925150 • Telebras</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-700/80 rounded-lg p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider">Valor Global Contratado</span>
              <div className="text-2xl font-black text-blue-400 mt-1">
                {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(
                  resumoAreas.total_valor_global || 0
                )}
              </div>
              <span className="text-[11px] text-slate-400">Total em execução contínua</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-700/80 rounded-lg p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider">Crítico: Vence em &lt; 30d</span>
              <div className="text-2xl font-black text-red-400 mt-1">
                {resumoAreas.total_criticos_30d}
              </div>
              <span className="text-[11px] text-red-400 font-medium">Risco de apagão contratual</span>
            </div>

            <div className="bg-slate-900/60 border border-slate-700/80 rounded-lg p-4">
              <span className="text-xs text-slate-400 uppercase tracking-wider">Alerta: Renovação &lt; 90d</span>
              <div className="text-2xl font-black text-amber-400 mt-1">
                {resumoAreas.total_alerta_90d}
              </div>
              <span className="text-[11px] text-amber-400 font-medium">Janela para aditivo/nova licitação</span>
            </div>
          </div>
        )}
      </div>

      {/* Navegação entre Abas do Módulo */}
      <div className="flex border-b border-slate-700 bg-slate-800/60 rounded-t-xl px-4 gap-2">
        <button
          onClick={() => setActiveSubTab('panorama')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'panorama'
              ? 'border-blue-500 text-blue-400 bg-blue-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>📋</span>
          <span>Contratos Vigentes &amp; Inferência IA</span>
          <span className="bg-slate-700 text-slate-300 text-[10px] px-2 py-0.5 rounded-full">
            {contratos.length}
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab('kanban_areas')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'kanban_areas'
              ? 'border-blue-500 text-blue-400 bg-blue-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>🏛️</span>
          <span>Kanban Multi-Áreas Telebras</span>
          <span className="bg-blue-600/30 text-blue-300 border border-blue-500/30 text-[10px] px-2 py-0.5 rounded-full">
            7 Áreas
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab('tempo_medio')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'tempo_medio'
              ? 'border-blue-500 text-blue-400 bg-blue-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>⏱️</span>
          <span>Tempo Médio pelas Áreas (Amostras)</span>
        </button>

        <button
          onClick={() => setActiveSubTab('paradigma')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'paradigma'
              ? 'border-blue-500 text-blue-400 bg-blue-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>🏆</span>
          <span>Processo Paradigma Encerrado no SIGA</span>
        </button>

        <button
          onClick={() => setActiveSubTab('estatistica')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'estatistica'
              ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>📈</span>
          <span>Inferência Estatística &amp; PERT</span>
          <span className="bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
            n=61 PEs • n=28 DEs
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab('capacidade_planejamento')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'capacidade_planejamento'
              ? 'border-amber-500 text-amber-400 bg-amber-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>⚡</span>
          <span>Agendador &amp; Capacidade GCC</span>
          <span className="bg-amber-600/30 text-amber-300 border border-amber-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
            Robô de Planejamento
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab('esteira_governanca')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'esteira_governanca'
              ? 'border-blue-500 text-blue-400 bg-blue-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>🏛️</span>
          <span>Esteira de Governança PLAC</span>
          <span className="bg-blue-600/30 text-blue-300 border border-blue-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
            5 Fases do Ciclo
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab('sentinela_planejamento')}
          className={`py-3 px-4 text-xs font-semibold border-b-2 flex items-center gap-2 transition ${
            activeSubTab === 'sentinela_planejamento'
              ? 'border-purple-500 text-purple-400 bg-purple-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <span>🤖</span>
          <span>Sentinela &amp; Telemetria PLAC</span>
          <span className="bg-purple-600/30 text-purple-300 border border-purple-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
            Auditoria IAC/ICNP
          </span>
        </button>
      </div>

      {/* ABA 1: PANORAMA & TABELA DE CONTRATOS */}
      {activeSubTab === 'panorama' && (
        <div className="space-y-6">
          {/* Stepper Visual das 7 Áreas */}
          {resumoAreas && (
            <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-5 shadow">
              <div className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-4 flex items-center gap-2">
                <span>🔄</span> Fluxo Lógico Interdepartamental pelas 7 Macro-Áreas da Telebras
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
                {resumoAreas.areas_fluxo.map((area, idx) => {
                  const isSelected = filtroArea === area.area_id;
                  return (
                    <button
                      key={area.area_id}
                      onClick={() => setFiltroArea(isSelected ? '' : area.area_id)}
                      className={`text-left p-3 rounded-lg border transition relative flex flex-col justify-between ${
                        isSelected
                          ? 'bg-blue-600/20 border-blue-500 shadow-md shadow-blue-500/10 ring-1 ring-blue-500'
                          : 'bg-slate-900/60 border-slate-700/80 hover:border-slate-600'
                      }`}
                    >
                      <div>
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-[10px] font-bold text-slate-400">PASSO {idx + 1}</span>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full font-bold ${
                              area.total_processos > 0
                                ? 'bg-blue-500/30 text-blue-300'
                                : 'bg-slate-800 text-slate-500'
                            }`}
                          >
                            {area.total_processos}
                          </span>
                        </div>
                        <p className="text-xs font-bold text-slate-100 line-clamp-1">{area.sigla}</p>
                        <p className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-tight">
                          {area.responsavel_padrao}
                        </p>
                      </div>

                      <div className="mt-3 pt-2 border-t border-slate-800 flex justify-between items-center text-[10px]">
                        <span className="text-slate-500">SLA: {area.sla_dias}d</span>
                        {area.total_criticos > 0 && (
                          <span className="text-red-400 font-bold">⚠️ {area.total_criticos}</span>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>

              {filtroArea && (
                <div className="mt-3 flex items-center justify-between text-xs bg-blue-500/10 border border-blue-500/20 px-3 py-1.5 rounded-lg text-blue-300">
                  <span>Filtrando pela área: <strong>{filtroArea.toUpperCase()}</strong></span>
                  <button onClick={() => setFiltroArea('')} className="underline hover:text-white">
                    Limpar Filtro
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Barra de Filtros */}
          <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 flex flex-wrap gap-3 items-center justify-between">
            <div className="flex-1 min-w-[240px]">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Buscar por Contrato, Processo SIGA, Fornecedor ou Objeto..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3.5 py-2 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
              />
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <select
                value={filtroVigencia}
                onChange={(e) => setFiltroVigencia(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="">Status da Vigência (Todos)</option>
                <option value="CRITICO_30D">🔴 Crítico (&lt; 30 dias)</option>
                <option value="ALERTA_90D">🟡 Alerta (&lt; 90 dias)</option>
                <option value="ATENCAO_180D">🔵 Atenção (&lt; 180 dias)</option>
                <option value="REGULAR">🟢 Regular (&gt; 180 dias)</option>
              </select>

              <select
                value={filtroModalidade}
                onChange={(e) => setFiltroModalidade(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
              >
                <option value="">Modalidade (Todas)</option>
                <option value="Pregão">Pregão Eletrônico</option>
                <option value="Dispensa">Dispensa de Licitação</option>
                <option value="Inexigibilidade">Inexigibilidade</option>
              </select>
            </div>
          </div>

          {/* Tabela de Contratos */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden shadow-xl">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-200">
                <thead className="bg-slate-850 border-b border-slate-700 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <tr>
                    <th className="py-3 px-4">Contrato &amp; Processo SIGA</th>
                    <th className="py-3 px-4">Objeto &amp; Fornecedor</th>
                    <th className="py-3 px-4">Modalidade &amp; Valor</th>
                    <th className="py-3 px-4">Vigência &amp; Dias Restantes</th>
                    <th className="py-3 px-4">Área Atual no SIGA</th>
                    <th className="py-3 px-4 text-center">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/60 font-sans">
                  {loading ? (
                    <tr>
                      <td colSpan="6" className="py-12 text-center text-slate-400">
                        Carregando contratos vigentes e tramitação do SIGA...
                      </td>
                    </tr>
                  ) : contratosFiltrados.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="py-12 text-center text-slate-400">
                        Nenhum contrato encontrado para os filtros selecionados.
                      </td>
                    </tr>
                  ) : (
                    contratosFiltrados.map((ctr) => (
                      <tr key={ctr.id} className="hover:bg-slate-750 transition">
                        <td className="py-3 px-4 align-top">
                          <div className="flex items-center gap-1.5 mb-1">
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                              🌐 PNCP • 🏛️ SIGA
                            </span>
                            {ctr.volume_siga && (
                              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-950/40 text-amber-300 border border-amber-500/30">
                                📑 {ctr.volume_siga}
                              </span>
                            )}
                          </div>
                          <div className="font-bold text-white flex items-center gap-1.5">
                            <span>📄</span> {ctr.numero_contrato}
                          </div>
                          <div className="text-[11px] text-blue-400 font-mono mt-0.5 font-semibold">
                            SIGA: {ctr.numero_processo_siga}
                          </div>
                          <div className="text-[10px] text-slate-400 mt-1">
                            Fiscal: <span className="text-slate-200 font-medium">{ctr.fiscal_titular || 'Designado'}</span>
                          </div>
                        </td>

                        <td className="py-3 px-4 align-top max-w-xs">
                          <p className="font-semibold text-slate-200 line-clamp-2">{ctr.objeto}</p>
                          <p className="text-[11px] text-slate-400 mt-1 font-mono">{ctr.fornecedor}</p>
                          <span className="text-[10px] text-slate-500 font-mono">CNPJ: {ctr.cnpj_cpf}</span>
                        </td>

                        <td className="py-3 px-4 align-top">
                          <span className="inline-block bg-slate-700 text-slate-300 text-[10px] px-2 py-0.5 rounded font-medium mb-1">
                            {ctr.modalidade}
                          </span>
                          <div className="font-bold text-white">
                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(
                              ctr.valor_global || 0
                            )}
                          </div>
                          <p className="text-[10px] text-slate-400">{ctr.fundamentacao_legal}</p>
                        </td>

                        <td className="py-3 px-4 align-top">
                          <div
                            className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full border text-[11px] font-bold ${getCorVigenciaBadge(
                              ctr.status_vigencia
                            )}`}
                          >
                            <span>⏳</span>
                            <span>{ctr.dias_restantes} dias restantes</span>
                          </div>
                          <div className="text-[11px] text-slate-400 mt-1.5">
                            Fim: <strong>{ctr.data_fim_vigencia}</strong>
                          </div>
                          <p className="text-[10px] text-slate-500 line-clamp-1">{ctr.alerta_vigencia}</p>
                        </td>

                        <td className="py-3 px-4 align-top">
                          <div className="bg-slate-900 border border-slate-700/80 rounded-lg p-2.5 space-y-1.5">
                            <div className="flex items-center justify-between text-[11px]">
                              <span className="font-bold text-slate-100 flex items-center gap-1">
                                <span>🏛️</span> {ctr.area_atual_nome}
                              </span>
                              <span className="text-slate-400 text-[10px]">({ctr.dias_na_area_atual}d na área)</span>
                            </div>
                            <div className="text-[10px] text-slate-400 border-t border-slate-800 pt-1">
                              <span className="font-semibold text-slate-400">📍 Onde: </span>
                              <span className="text-slate-300 font-mono">{ctr.localizacao_atual || 'Mesa Virtual SIGA'}</span>
                            </div>
                            <div className="text-[10px] text-slate-400">
                              <span className="font-semibold text-slate-400">👤 Com quem: </span>
                              <span className="text-amber-400 font-medium">{ctr.custodiante_atual || ctr.fiscal_titular || 'Fiscal Designado'}</span>
                            </div>
                            <p className="text-[10px] text-slate-400 border-t border-slate-800 pt-1 line-clamp-2">
                              {ctr.ultimo_despacho_siga}
                            </p>
                          </div>
                        </td>

                        <td className="py-3 px-4 align-top text-center space-y-2">
                          <button
                            onClick={() => abrirInferenciaIA(ctr.id)}
                            className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-medium text-[11px] py-1.5 px-2.5 rounded-lg shadow transition flex items-center justify-center gap-1.5"
                          >
                            <span>🤖</span> Inferir Caminho IA
                          </button>

                          {ctr.link_pncp && (
                            <a
                              href={ctr.link_pncp}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="w-full bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-300 text-[11px] py-1 px-2 rounded-lg border border-cyan-500/30 transition flex items-center justify-center gap-1 font-semibold"
                              title={ctr.link_pncp.includes('?q=') ? "Consultar acervo de contratações da Telebras no PNCP" : "Abrir Contrato Oficial no Portal Nacional de Contratações Públicas (PNCP)"}
                            >
                              <span>🌐 {ctr.link_pncp.includes('?q=') ? "Consultar no PNCP" : "Ver no PNCP"}</span>
                              <span>↗</span>
                            </a>
                          )}

                          <button
                            onClick={() =>
                              setProcessoDocumentosModal({
                                id: ctr.id,
                                numero_processo_siga: ctr.numero_processo_siga,
                                objeto: ctr.objeto
                              })
                            }
                            className="w-full bg-slate-700 hover:bg-slate-600 text-slate-200 text-[11px] py-1 px-2 rounded-lg border border-slate-600 transition flex items-center justify-center gap-1"
                          >
                            <span>📎</span> Docs SIGA
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ABA 2: KANBAN MULTI-ÁREAS TELEBRAS (7 COLUNAS) */}
      {activeSubTab === 'kanban_areas' && (
        <div className="space-y-4">
          <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-4 flex justify-between items-center">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <span>🏛️</span> Kanban Interdepartamental: Rastreamento pelas 7 Áreas da Telebras
              </h2>
              <p className="text-xs text-slate-400">
                Visualização do fluxo contínuo de processos e contratos ativos distribuídos por gerência e diretoria.
              </p>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> No Prazo
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500 ml-2"></span> Alerta de SLA
              <span className="w-2.5 h-2.5 rounded-full bg-red-500 ml-2"></span> Estourado
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-7 gap-3 overflow-x-auto pb-4">
            {kanbanAreas.map((coluna) => (
              <div
                key={coluna.id}
                className="bg-slate-850 border border-slate-700/80 rounded-xl flex flex-col min-w-[230px]"
              >
                {/* Header da Coluna */}
                <div className="p-3 border-b border-slate-700 bg-slate-800/90 rounded-t-xl">
                  <div className="flex justify-between items-center">
                    <span className="text-xs font-bold text-white">{coluna.sigla}</span>
                    <span className="bg-blue-600/20 text-blue-300 border border-blue-500/30 text-[10px] font-bold px-2 py-0.5 rounded-full">
                      {coluna.total_cards}
                    </span>
                  </div>
                  <p className="text-[10px] text-slate-400 mt-0.5 line-clamp-1">{coluna.nome}</p>
                  <div className="text-[10px] text-slate-500 mt-1">SLA: {coluna.sla_dias} dias úteis</div>
                </div>

                {/* Cards da Coluna */}
                <div className="p-2 space-y-2.5 flex-1 min-h-[300px]">
                  {coluna.cards.length === 0 ? (
                    <div className="h-full flex items-center justify-center text-center p-4 text-[11px] text-slate-500 border border-dashed border-slate-750 rounded-lg">
                      Nenhum processo retido nesta estação no momento
                    </div>
                  ) : (
                    coluna.cards.map((card) => (
                      <div
                        key={card.id}
                        className="bg-slate-800 hover:bg-slate-750 border border-slate-700 rounded-lg p-3 shadow-md transition group space-y-1.5"
                      >
                        <div className="flex items-center justify-between gap-1">
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                            PNCP • SIGA
                          </span>
                          <span
                            className={`text-[9px] px-1.5 py-0.5 rounded font-semibold ${
                              card.dias_restantes <= 30
                                ? 'bg-red-500/20 text-red-300'
                                : card.dias_restantes <= 90
                                ? 'bg-amber-500/20 text-amber-300'
                                : 'bg-emerald-500/20 text-emerald-300'
                            }`}
                          >
                            ⏳ {card.dias_restantes}d
                          </span>
                        </div>

                        <div className="flex justify-between items-start">
                          <span className="text-[11px] font-bold text-white font-mono truncate">
                            📄 {card.numero_contrato}
                          </span>
                          {card.volume_siga && (
                            <span className="text-[9px] text-amber-300 font-mono bg-amber-950/40 px-1 rounded border border-amber-500/20">
                              📑 {card.volume_siga}
                            </span>
                          )}
                        </div>

                        <div className="text-[10px] text-blue-400 font-mono font-medium">
                          Proc: {card.numero_processo_siga}
                        </div>

                        <p className="text-[11px] text-slate-200 line-clamp-2 font-medium leading-tight">{card.objeto}</p>

                        {/* Onde e Com quem */}
                        <div className="bg-slate-900/70 border border-slate-750 p-1.5 rounded text-[9px] space-y-0.5 text-slate-400">
                          <div>
                            <span className="text-slate-500 font-semibold">📍 Onde:</span>{' '}
                            <span className="text-slate-300 font-mono">{card.localizacao_atual || card.area_atual_nome}</span>
                          </div>
                          <div>
                            <span className="text-slate-500 font-semibold">👤 Com quem:</span>{' '}
                            <span className="text-amber-400 font-semibold">{card.custodiante_atual || card.fiscal_titular || 'Fiscal Designado'}</span>
                          </div>
                        </div>

                        <div className="text-[10px] text-slate-400 flex justify-between items-center font-mono pt-1 border-t border-slate-700/40">
                          <span className="truncate max-w-[100px]">{card.fornecedor?.substring(0, 14)}...</span>
                          <span className="text-white font-bold">
                            {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(
                              card.valor_global || 0
                            )}
                          </span>
                        </div>

                        <div className="pt-1 border-t border-slate-700/60 flex items-center justify-between text-[10px]">
                          {card.link_pncp ? (
                            <a
                              href={card.link_pncp}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-cyan-400 hover:text-cyan-300 text-[10px] font-semibold flex items-center gap-0.5"
                              title="Abrir no PNCP"
                            >
                              <span>🌐 PNCP ↗</span>
                            </a>
                          ) : (
                            <span className="text-slate-500">Há {card.dias_na_area_atual}d</span>
                          )}

                          <button
                            onClick={() => abrirInferenciaIA(card.id)}
                            className="text-blue-400 hover:text-blue-300 font-medium underline text-[10px]"
                          >
                            Próximo Passo ➔
                          </button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ABA 3: TEMPO MÉDIO PELAS ÁREAS & AMOSTRAS DE PROCESSOS */}
      {activeSubTab === 'tempo_medio' && metricasTempo && (
        <div className="space-y-6">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <span>⏱️</span> Análise de Tempo Médio de Tramitação pelas Áreas da Telebras
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Métricas consolidadas a partir de uma amostra de <strong>{metricasTempo.amostras_analisadas} processos</strong> autuados e finalizados no SIGA, contrastando o Lead Time real com o SLA estipulado no Anexo III da Diretriz do PLAC.
            </p>

            {/* Indicadores Resumo */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 mt-5">
              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider">Tempo Médio Total Real</span>
                <div className="text-2xl font-black text-white mt-1">
                  {metricasTempo.tempo_medio_total_dias_uteis} dias úteis
                </div>
                <span className="text-[11px] text-emerald-400">Vs Meta SLA de {metricasTempo.sla_medio_referencia} dias</span>
              </div>

              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider">Ganho de Eficiência</span>
                <div className="text-2xl font-black text-emerald-400 mt-1">
                  - {metricasTempo.ganho_eficiencia_dias} dias úteis
                </div>
                <span className="text-[11px] text-slate-400">Economia no ciclo total</span>
              </div>

              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider">Taxa de Conformidade SLA</span>
                <div className="text-2xl font-black text-blue-400 mt-1">
                  {metricasTempo.taxa_conformidade_sla_pct}%
                </div>
                <span className="text-[11px] text-blue-400">Processos finalizados no prazo</span>
              </div>

              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider">Maior Ponto de Retenção</span>
                <div className="text-2xl font-black text-amber-400 mt-1">
                  GCC (22.4d)
                </div>
                <span className="text-[11px] text-amber-300">Pesquisa de Preços IN 65</span>
              </div>
            </div>

            {/* Tabela de Lead Time por Área */}
            <div className="mt-6 border border-slate-700 rounded-xl overflow-hidden">
              <table className="w-full text-left text-xs text-slate-200">
                <thead className="bg-slate-850 text-slate-400 font-semibold uppercase tracking-wider text-[11px] border-b border-slate-700">
                  <tr>
                    <th className="py-3 px-4">Estação / Área da Telebras</th>
                    <th className="py-3 px-4">Tempo Médio Real</th>
                    <th className="py-3 px-4">Meta SLA (Anexo III)</th>
                    <th className="py-3 px-4">Desvio / Status</th>
                    <th className="py-3 px-4">Principal Fator de Retenção</th>
                    <th className="py-3 px-4 text-center">Taxa de Saneamento</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700/60 font-sans">
                  {metricasTempo.distribuicao_tempo_areas.map((item) => {
                    const diff = item.tempo_medio_dias - item.sla_meta;
                    return (
                      <tr key={item.area_id} className="hover:bg-slate-750 transition">
                        <td className="py-3 px-4 font-bold text-white">
                          {item.nome}
                        </td>
                        <td className="py-3 px-4 font-bold text-blue-400">
                          {item.tempo_medio_dias} dias úteis
                        </td>
                        <td className="py-3 px-4 text-slate-400">
                          {item.sla_meta} dias úteis
                        </td>
                        <td className="py-3 px-4">
                          {diff > 0 ? (
                            <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
                              ⚠️ +{diff.toFixed(1)}d (Gargalo)
                            </span>
                          ) : (
                            <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
                              ✅ {diff.toFixed(1)}d (Otimizado)
                            </span>
                          )}
                        </td>
                        <td className="py-3 px-4 text-slate-300">
                          {item.fator_retencao}
                        </td>
                        <td className="py-3 px-4 text-center">
                          <span className="text-slate-300 font-medium">{item.taxa_saneamento_pct}%</span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* ABA 4: PROCESSO PARADIGMA ENCERRADO NO SIGA */}
      {activeSubTab === 'paradigma' && paradigma && (
        <div className="space-y-6">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-700 pb-5">
              <div>
                <span className="bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs px-2.5 py-1 rounded-full font-bold">
                  Estudo de Caso Paradigma • Ciclo Completo
                </span>
                <h2 className="text-lg font-bold text-white mt-2 flex items-center gap-2">
                  Processo nº {paradigma.numero_processo} • Contrato {paradigma.numero_contrato}
                </h2>
                <p className="text-xs text-slate-400 mt-1 max-w-3xl">
                  {paradigma.objeto}
                </p>
              </div>

              <div className="text-right">
                <span className="text-xs text-slate-400">Resultado da Tramitação:</span>
                <div className="text-sm font-bold text-emerald-400 mt-0.5">
                  ✅ {paradigma.resultado_tramitacao}
                </div>
                <div className="text-xs text-blue-400 font-mono mt-1">
                  Tempo Total: <strong>{paradigma.dias_totais_tramitacao} dias úteis</strong> (Meta: {paradigma.sla_meta_dias}d)
                </div>
              </div>
            </div>

            {/* Linha do Tempo Sequencial das 7 Fases */}
            <div className="mt-8 space-y-6 relative before:absolute before:inset-0 before:left-8 before:w-0.5 before:bg-slate-700">
              {paradigma.fases_percorridas.map((fase) => (
                <div key={fase.etapa} className="relative flex items-start gap-6 group">
                  {/* Ponto / Ícone */}
                  <div className="w-16 h-16 rounded-full bg-slate-900 border-2 border-blue-500 flex items-center justify-center font-bold text-white text-sm shadow-lg shadow-blue-500/20 z-10 shrink-0">
                    #{fase.etapa}
                  </div>

                  {/* Conteúdo da Fase */}
                  <div className="flex-1 bg-slate-900/90 border border-slate-700 rounded-xl p-5 shadow-md">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                      <div>
                        <h3 className="text-sm font-bold text-white flex items-center gap-2">
                          {fase.area}
                          <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] px-2 py-0.5 rounded-full font-bold">
                            {fase.dias_uteis} dias úteis (SLA: {fase.sla_etapa}d)
                          </span>
                        </h3>
                        <p className="text-xs text-slate-400 mt-0.5">
                          Responsável: <strong className="text-slate-300">{fase.responsavel}</strong> • Período: {fase.entrada} até {fase.saida}
                        </p>
                      </div>

                      <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded font-mono border border-slate-700">
                        Despacho no SIGA
                      </span>
                    </div>

                    <div className="mt-3 bg-slate-800/70 border border-slate-700/60 rounded-lg p-3 text-xs text-slate-200 font-sans">
                      <p className="leading-relaxed">"{fase.despacho}"</p>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                      {fase.documentos.map((doc, dIdx) => (
                        <span
                          key={dIdx}
                          className="bg-blue-900/30 text-blue-300 border border-blue-800/40 text-[10px] px-2.5 py-1 rounded-md flex items-center gap-1.5"
                        >
                          <span>📎</span> {doc}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ABA 5: INFERÊNCIA ESTATÍSTICA & PERT (AMOSTRAS REAIS) */}
      {activeSubTab === 'estatistica' && dadosEstatisticos && (
        <div className="space-y-6">
          {/* Header do Módulo Estatístico */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl relative overflow-hidden">
            <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl pointer-events-none" />
            <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
              <div>
                <span className="bg-emerald-600/30 text-emerald-300 border border-emerald-500/30 text-xs px-2.5 py-1 rounded-full font-bold">
                  Estatística Amostral Rigorosa • Teorema Central do Limite
                </span>
                <h2 className="text-lg font-bold text-white mt-2 flex items-center gap-2">
                  <span>📈</span> Inferência Estatística Amostral &amp; Calibração da Planilha GCC
                </h2>
                <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
                  Análise probabilística fundamentada em <strong>61 Pregões Eletrônicos</strong> e <strong>28 Dispensas de Licitação</strong> reais e auditáveis da Telebras. Como o SIGA opera na intranet interna, a inferência amostral calibra a <strong>Planilha Oficial da GCC</strong> (144 dias) com a realidade operacional (média de 30,4 dias úteis).
                </p>
              </div>

              <div className="flex items-center gap-2 text-xs">
                <span className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 font-mono text-emerald-400 font-bold">
                  IC 95%: [26.07d, 34.78d]
                </span>
              </div>
            </div>

            {/* Cards de Métricas Amostrais Resumo */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Média Real Telebras (Pregão)</span>
                <div className="text-2xl font-black text-emerald-400 mt-1">
                  {Math.ceil(dadosEstatisticos.pregao_eletronico.estatistica_amostral.media_dias_uteis)} dias úteis
                </div>
                <span className="text-[11px] text-slate-400">
                  Margem de erro: ±{dadosEstatisticos.pregao_eletronico.estatistica_amostral.ic_95.margem_erro}d (n=61 certames)
                </span>
              </div>

              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Planilha Oficial GCC (Teórica)</span>
                <div className="text-2xl font-black text-amber-400 mt-1">
                  {Math.ceil(dadosEstatisticos.pregao_eletronico.prazo_teorico_planilha_gcc)} dias úteis
                </div>
                <span className="text-[11px] text-amber-300">
                  Pior caso cumulativo (4.7x mais conservador)
                </span>
              </div>

              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Previsão PERT (Certeza 80%)</span>
                <div className="text-2xl font-black text-blue-400 mt-1">
                  {Math.ceil(dadosEstatisticos.pregao_eletronico.modelo_pert.percentis.p80_certeza_80pct)} dias úteis
                </div>
                <span className="text-[11px] text-blue-300">
                  Recomendado para baseline do PLAC
                </span>
              </div>

              <div className="bg-slate-900/80 border border-slate-700 rounded-lg p-4">
                <span className="text-[11px] text-slate-400 uppercase tracking-wider font-semibold">Dispensa de Licitação (Média)</span>
                <div className="text-2xl font-black text-purple-400 mt-1">
                  {Math.ceil(dadosEstatisticos.dispensa_licitacao.estatistica_amostral.media_dias_uteis)} dias úteis
                </div>
                <span className="text-[11px] text-purple-300">
                  Mediana: {Math.ceil(dadosEstatisticos.dispensa_licitacao.estatistica_amostral.mediana_dias)}d (vs 117d na GCC)
                </span>
              </div>
            </div>
          </div>

          {/* Comparador Visual de Modelos de Duração */}
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl space-y-5">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-700 pb-3">
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>📊</span> Comparativo de Modelos: Teórico GCC vs. Distribuição Empírica PERT
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Visualização em escala dos prazos de Pregão Eletrônico (em dias úteis até homologação).
                </p>
              </div>
              <span className="text-xs text-slate-400 font-mono">
                Escala: 0 a 144 dias úteis
              </span>
            </div>

            <div className="space-y-4 pt-2">
              {/* Barra 1: GCC Oficial */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-amber-300 flex items-center gap-1.5">
                    <span>🔴</span> Planilha Oficial GCC (Regimental / Teto de Risco)
                  </span>
                  <span className="text-amber-400 font-mono font-bold">144 dias úteis</span>
                </div>
                <div className="h-5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-700">
                  <div className="h-full bg-gradient-to-r from-amber-600 to-red-600 rounded-full w-full flex items-center justify-end pr-2 text-[10px] text-white font-bold">
                    100% (Teto Cumulativo)
                  </div>
                </div>
              </div>

              {/* Barra 2: Outlier Máximo Histórico */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-orange-300 flex items-center gap-1.5">
                    <span>⚠️</span> Pior Caso Histórico Real (Outlier com Múltiplas Impugnações)
                  </span>
                  <span className="text-orange-400 font-mono font-bold">101 dias úteis</span>
                </div>
                <div className="h-5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-700">
                  <div className="h-full bg-orange-600 rounded-full flex items-center justify-end pr-2 text-[10px] text-white font-bold" style={{ width: `${(101/144)*100}%` }}>
                    101d (70.1%)
                  </div>
                </div>
              </div>

              {/* Barra 3: PERT P95 */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-purple-300 flex items-center gap-1.5">
                    <span>🟣</span> PERT P95 (Alta Certeza - 95% dos certames concluem antes)
                  </span>
                  <span className="text-purple-400 font-mono font-bold">43 dias úteis</span>
                </div>
                <div className="h-5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-700">
                  <div className="h-full bg-purple-600 rounded-full flex items-center justify-end pr-2 text-[10px] text-white font-bold" style={{ width: `${(43/144)*100}%` }}>
                    43d (29.9%)
                  </div>
                </div>
              </div>

              {/* Barra 4: PERT P80 (Recomendado) */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-blue-300 flex items-center gap-1.5">
                    <span>🔵</span> PERT P80 (Recomendado PLAC - Certeza Padrão de 80%)
                  </span>
                  <span className="text-blue-400 font-mono font-bold">37 dias úteis</span>
                </div>
                <div className="h-5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-700">
                  <div className="h-full bg-blue-600 rounded-full flex items-center justify-end pr-2 text-[10px] text-white font-bold" style={{ width: `${(37/144)*100}%` }}>
                    37d (25.7%)
                  </div>
                </div>
              </div>

              {/* Barra 5: Média Real Empírica */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-emerald-300 flex items-center gap-1.5">
                    <span>🟢</span> Média Histórica Real da Telebras (n=61 certames)
                  </span>
                  <span className="text-emerald-400 font-mono font-bold">31 dias úteis</span>
                </div>
                <div className="h-5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-700">
                  <div className="h-full bg-emerald-500 rounded-full flex items-center justify-end pr-2 text-[10px] text-white font-bold" style={{ width: `${(31/144)*100}%` }}>
                    31d (21.5%)
                  </div>
                </div>
              </div>

              {/* Barra 6: Mediana */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs font-semibold">
                  <span className="text-cyan-300 flex items-center gap-1.5">
                    <span>🎯</span> Mediana Histórica Real (50% dos certames concluem antes)
                  </span>
                  <span className="text-cyan-400 font-mono font-bold">27 dias úteis</span>
                </div>
                <div className="h-5 w-full bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-700">
                  <div className="h-full bg-cyan-500 rounded-full flex items-center justify-end pr-2 text-[10px] text-white font-bold" style={{ width: `${(27/144)*100}%` }}>
                    27d (18.8%)
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Grid de Tabelas e Diagnóstico */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Tabela de Parâmetros Estatísticos Formais */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-xl space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>📋</span> Parâmetros Estatísticos Rigorosos (Amostras Reais)
              </h3>

              <div className="overflow-x-auto border border-slate-700 rounded-lg">
                <table className="w-full text-left text-xs text-slate-200">
                  <thead className="bg-slate-850 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-700">
                    <tr>
                      <th className="py-2.5 px-3">Parâmetro Estatístico</th>
                      <th className="py-2.5 px-3 text-right">Pregão Eletrônico</th>
                      <th className="py-2.5 px-3 text-right">Dispensa Licitação</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/60 font-mono text-xs">
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Tamanho da Amostra (n)</td>
                      <td className="py-2 px-3 text-right font-bold text-white">61 certames</td>
                      <td className="py-2 px-3 text-right font-bold text-white">28 certames</td>
                    </tr>
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Média Amostral (x̄)</td>
                      <td className="py-2 px-3 text-right font-bold text-emerald-400">31 dias</td>
                      <td className="py-2 px-3 text-right font-bold text-emerald-400">16 dias</td>
                    </tr>
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Desvio Padrão Amostral (s)</td>
                      <td className="py-2 px-3 text-right text-blue-300">17.35 dias</td>
                      <td className="py-2 px-3 text-right text-blue-300">12.65 dias</td>
                    </tr>
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Variância Amostral (s²)</td>
                      <td className="py-2 px-3 text-right text-slate-400">301.07</td>
                      <td className="py-2 px-3 text-right text-slate-400">160.03</td>
                    </tr>
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Mediana (Md)</td>
                      <td className="py-2 px-3 text-right text-cyan-300 font-bold">27 dias</td>
                      <td className="py-2 px-3 text-right text-cyan-300 font-bold">12 dias</td>
                    </tr>
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Mínimo / Máximo</td>
                      <td className="py-2 px-3 text-right text-slate-300">8d / 101d</td>
                      <td className="py-2 px-3 text-right text-slate-300">3d / 52d</td>
                    </tr>
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Erro Padrão da Média (SE)</td>
                      <td className="py-2 px-3 text-right text-amber-300">± 2.22 dias</td>
                      <td className="py-2 px-3 text-right text-amber-300">± 2.39 dias</td>
                    </tr>
                    <tr className="hover:bg-slate-750 bg-blue-950/20">
                      <td className="py-2 px-3 text-slate-200 font-sans font-semibold">Intervalo de Confiança 95%</td>
                      <td className="py-2 px-3 text-right text-emerald-300 font-bold">[26.07d, 34.78d]</td>
                      <td className="py-2 px-3 text-right text-emerald-300 font-bold">[10.95d, 20.33d]</td>
                    </tr>
                    <tr className="hover:bg-slate-750">
                      <td className="py-2 px-3 text-slate-300 font-sans">Coeficiente de Variação (CV)</td>
                      <td className="py-2 px-3 text-right text-purple-300 font-bold">57.0%</td>
                      <td className="py-2 px-3 text-right text-purple-300 font-bold">80.9%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Diagnóstico de Calibração da GCC */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-xl space-y-4">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>🔍</span> Por que a Planilha GCC prevê 144 dias?
              </h3>

              <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
                <div className="p-3.5 bg-slate-900 border border-slate-700 rounded-lg">
                  <div className="font-bold text-amber-400 mb-1 flex items-center gap-1.5">
                    <span>⚠️</span> Modelo de Pior Caso Cumulativo (Overestimation)
                  </div>
                  <p>
                    A planilha oficial da GCC soma aritmeticamente os prazos máximos regimentais de todas as 7 áreas da Telebras e reserva <strong>25 dias úteis adicionais para fase recursal</strong>.
                  </p>
                </div>

                <div className="p-3.5 bg-slate-900 border border-slate-700 rounded-lg">
                  <div className="font-bold text-emerald-400 mb-1 flex items-center gap-1.5">
                    <span>✅</span> A Realidade Operacional (74% sem recursos)
                  </div>
                  <p>
                    Na prática, <strong>74% dos pregões da Telebras não sofrem recursos administrativos</strong>, tramitando diretamente da sessão pública para a homologação em média de 17 dias úteis.
                  </p>
                </div>

                <div className="p-3.5 bg-blue-950/30 border border-blue-500/30 rounded-lg">
                  <div className="font-bold text-blue-300 mb-1 flex items-center gap-1.5">
                    <span>🎯</span> Recomendação de Governança PLAC
                  </div>
                  <p>
                    Adotar o <strong>percentil P80 (37 dias úteis)</strong> como a baseline oficial de planejamento e metas da empresa, mantendo o SLA de 144 dias da GCC apenas como limite de conformidade legal.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* SIMULADOR INTERATIVO DE PREVISÃO PROBABILÍSTICA EM TEMPO REAL */}
          <div className="bg-gradient-to-br from-slate-850 via-slate-800 to-slate-850 border border-emerald-500/40 rounded-xl p-6 shadow-2xl space-y-6">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 border-b border-slate-700 pb-4">
              <div>
                <span className="bg-blue-600/30 text-blue-300 border border-blue-500/30 text-[10px] px-2.5 py-0.5 rounded-full font-bold uppercase tracking-wider">
                  Simulador Paramétrico
                </span>
                <h3 className="text-base font-bold text-white mt-1 flex items-center gap-2">
                  <span>🧮</span> Previsão Probabilística de Tempo Restante para Qualquer Processo
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Selecione o tipo de contratação, a etapa em que o processo se encontra e o nível de confiança estatística desejado.
                </p>
              </div>

              {simResultado && (
                <div className="text-right">
                  <span className="text-[11px] text-slate-400">Progresso do Processo:</span>
                  <div className="text-lg font-black text-emerald-400 font-mono">
                    {simResultado.progresso_pct}% concluído
                  </div>
                </div>
              )}
            </div>

            {/* Controles do Simulador */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              {/* Controle 1: Modalidade */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300">1. Modalidade de Contratação (10 Esteiras GCC):</label>
                <select
                  value={simTipo}
                  onChange={(e) => { setSimTipo(e.target.value); setSimEtapa(1); }}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg py-2.5 px-3 text-xs text-white font-medium focus:ring-1 focus:ring-blue-500 focus:border-blue-500 cursor-pointer"
                >
                  <optgroup label="Licitação Aberta">
                    <option value="PREGAO">Pregão Eletrônico (36/40 Etapas - Dec. 10.024)</option>
                  </optgroup>
                  <optgroup label="Dispensas de Licitação (Art. 29 Lei 13.303)">
                    <option value="DISPENSA_TRADICIONAL">Dispensa Tradicional (32 Etapas - Art. 29 c/c 73)</option>
                    <option value="DISPENSA_BAIXO_VALOR">Dispensa Tradic. Baixo Valor (32 Etapas - Art. 29, I/II)</option>
                    <option value="DISPENSA_ELETRONICA">Dispensa Eletrônica Comprasnet (36 Etapas - IN 67/2021)</option>
                    <option value="DISPENSA_LOCACAO">Dispensa Locação de Imóveis/PoPs (19 Etapas - Parecer Padrão)</option>
                    <option value="DISPENSA_ENERGIA">Dispensa Concessionária Energia (21 Etapas - Termo Adesão)</option>
                  </optgroup>
                  <optgroup label="Inexigibilidades (Art. 30 Lei 13.303)">
                    <option value="INEXIGIBILIDADE_GERAL">Inexigibilidade Geral (31 Etapas - Fornecedor Exclusivo)</option>
                    <option value="INEXIGIBILIDADE_CURSOS">Inexigibilidade Cursos/Capacitação (15 Etapas - Parecer Padrão)</option>
                    <option value="INEXIGIBILIDADE_COMPARTILHAMENTO">Inexigibilidade Compartilhamento Infra (23 Etapas)</option>
                  </optgroup>
                  <optgroup label="Contratação Direta Especial">
                    <option value="AFASTAMENTO">Afastamento de Licitação (30 Etapas - Prática nº 88 / Art. 28 §3º)</option>
                  </optgroup>
                </select>
              </div>

              {/* Controle 2: Etapa Atual */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="text-xs font-bold text-slate-300">2. Etapa Atual no SIGA:</label>
                  <span className="text-xs text-blue-400 font-bold font-mono">
                    Etapa {simEtapa} de {simResultado?.total_etapas || 32}
                  </span>
                </div>
                <input
                  type="range"
                  min="1"
                  max={simResultado?.total_etapas || 32}
                  value={simEtapa}
                  onChange={(e) => setSimEtapa(parseInt(e.target.value))}
                  className="w-full accent-blue-500 cursor-pointer"
                />
                <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                  <span>Início (DOD/DFD)</span>
                  <span>Meio (Pesquisa/Minutas)</span>
                  <span>Fim (Assinatura)</span>
                </div>
              </div>

              {/* Controle 3: Nível de Certeza Estatística */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-slate-300">3. Grau de Certeza Estatística:</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setSimConfianca(50)}
                    className={`py-2 px-2 rounded-lg text-xs font-bold border transition text-center ${
                      simConfianca === 50
                        ? 'bg-cyan-600 text-white border-cyan-400 shadow'
                        : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-750'
                    }`}
                  >
                    50% (P50)
                  </button>
                  <button
                    onClick={() => setSimConfianca(80)}
                    className={`py-2 px-2 rounded-lg text-xs font-bold border transition text-center ${
                      simConfianca === 80
                        ? 'bg-blue-600 text-white border-blue-400 shadow ring-1 ring-blue-400'
                        : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-750'
                    }`}
                  >
                    80% (P80 ★)
                  </button>
                  <button
                    onClick={() => setSimConfianca(95)}
                    className={`py-2 px-2 rounded-lg text-xs font-bold border transition text-center ${
                      simConfianca === 95
                        ? 'bg-purple-600 text-white border-purple-400 shadow'
                        : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-750'
                    }`}
                  >
                    95% (P95)
                  </button>
                </div>
              </div>
            </div>

            {/* Resultado do Cálculo do Simulador */}
            {loadingSim ? (
              <div className="p-8 text-center text-slate-400">
                <div className="animate-spin text-2xl inline-block mb-2">⚙️</div>
                <p className="text-xs">Calculando distribuição probabilística PERT...</p>
              </div>
            ) : simResultado ? (
              <div className="bg-slate-900/90 border border-slate-700 rounded-xl p-5 space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="bg-slate-850 border border-slate-750 p-3.5 rounded-lg">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Dias Restantes (PERT)</span>
                    <div className="text-2xl font-black text-emerald-400 mt-0.5">
                      ~ {Math.ceil(simResultado.dias_uteis_restantes_pert)} dias úteis
                    </div>
                    <span className="text-[10px] text-emerald-300 font-mono">
                      Certeza: {simResultado.rotulo_confianca}
                    </span>
                  </div>

                  <div className="bg-slate-850 border border-slate-750 p-3.5 rounded-lg">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Data Prevista de Conclusão</span>
                    <div className="text-xl font-black text-white mt-1 font-mono">
                      {new Date(simResultado.data_projetada_conclusao_pert + 'T00:00:00').toLocaleDateString('pt-BR')}
                    </div>
                    <span className="text-[10px] text-slate-400">
                      Considerando dias úteis vigentes
                    </span>
                  </div>

                  <div className="bg-slate-850 border border-slate-750 p-3.5 rounded-lg">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Prazo Restante na GCC</span>
                    <div className="text-2xl font-black text-amber-400 mt-0.5">
                      {simResultado.dias_uteis_restantes_oficial_gcc} dias úteis
                    </div>
                    <span className="text-[10px] text-amber-300 font-mono">
                      {new Date(simResultado.data_projetada_conclusao_gcc + 'T00:00:00').toLocaleDateString('pt-BR')}
                    </span>
                  </div>

                  <div className="bg-slate-850 border border-slate-750 p-3.5 rounded-lg">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">Ganho de Eficiência Real</span>
                    <div className="text-2xl font-black text-blue-400 mt-0.5">
                      - {simResultado.ganho_eficiencia_dias_uteis} dias úteis
                    </div>
                    <span className="text-[10px] text-blue-300">
                      Economia vs teto da planilha GCC
                    </span>
                  </div>
                </div>

                {/* Mensagem Executiva de Previsão */}
                <div className="p-3.5 bg-blue-950/30 border border-blue-500/30 rounded-lg text-xs text-slate-200 flex items-center gap-3">
                  <span className="text-xl">💡</span>
                  <div className="leading-relaxed">
                    <strong>Parecer Gerencial:</strong> {simResultado.mensagem_previsao}
                  </div>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      )}

      {/* ABA 6: AGENDADOR DE CAPACIDADE DA GCC & CRONOGRAMA REVERSO (ROBÔ 1) */}
      {activeSubTab === 'capacidade_planejamento' && (
        <div className="space-y-6">
          <PlanejamentoCapacidadeWidget />
        </div>
      )}

      {/* DRAWER / MODAL DE INFERÊNCIA PREDITIVA DA IA */}
      {showInferenciaModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex justify-end animate-fadeIn">
          <div className="w-full max-w-2xl bg-slate-850 h-full border-l border-slate-700 shadow-2xl flex flex-col overflow-hidden">
            {/* Header Modal */}
            <div className="bg-slate-800 border-b border-slate-700 p-5 flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg text-lg">
                  🤖
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">Inferência Preditiva de Tramitação (IA)</h3>
                  <p className="text-xs text-slate-400">Projeção lógica de caminho pelas áreas da Telebras e recomendações</p>
                </div>
              </div>
              <button
                onClick={() => setShowInferenciaModal(false)}
                className="text-slate-400 hover:text-white text-lg p-1.5 rounded-lg hover:bg-slate-700 transition"
              >
                ✕
              </button>
            </div>

            {/* Conteúdo do Drawer */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {loadingInferencia ? (
                <div className="py-20 text-center text-slate-400 space-y-3">
                  <div className="animate-spin text-3xl">⚙️</div>
                  <p className="text-xs">Processando histórico do SIGA e calculando inferência...</p>
                </div>
              ) : inferenciaSelecionada ? (
                <>
                  {/* Ficha do Contrato */}
                  <div className="bg-slate-900 border border-slate-700/80 rounded-xl p-4">
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
                      Contrato PNCP &amp; Processo SIGA
                    </span>
                    <h4 className="text-sm font-bold text-white mt-1">
                      {inferenciaSelecionada.contrato?.numero_contrato} • {inferenciaSelecionada.contrato?.numero_processo_siga}
                    </h4>
                    <p className="text-xs text-slate-300 mt-1 line-clamp-2">
                      {inferenciaSelecionada.contrato?.objeto}
                    </p>
                    <div className="mt-3 pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
                      <span className="text-slate-400">Fornecedor: <strong className="text-white">{inferenciaSelecionada.contrato?.fornecedor}</strong></span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${getCorVigenciaBadge(inferenciaSelecionada.contrato?.status_vigencia)}`}>
                        {inferenciaSelecionada.contrato?.dias_restantes} dias restantes
                      </span>
                    </div>
                  </div>

                  {/* Diagnóstico da Área Atual */}
                  <div className="bg-slate-800/90 border border-slate-700 rounded-xl p-4 space-y-2">
                    <span className="text-[10px] text-blue-400 uppercase tracking-wider font-bold">
                      Localização Atual no SIGA
                    </span>
                    <div className="text-sm font-bold text-white flex items-center justify-between">
                      <span>{inferenciaSelecionada.onde_esta}</span>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                        inferenciaSelecionada.status_sla === 'ESTOURADO'
                          ? 'bg-red-500/20 text-red-300 border border-red-500/30'
                          : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      }`}>
                        {inferenciaSelecionada.msg_sla}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">
                      Último Despacho: <em>"{inferenciaSelecionada.contrato?.ultimo_despacho_siga}"</em>
                    </p>
                  </div>

                  {/* Projeção do Próximo Destino (Inferência IA) */}
                  <div className="bg-gradient-to-br from-blue-900/40 via-indigo-950/40 to-slate-900 border border-blue-500/40 rounded-xl p-5 shadow-xl relative overflow-hidden">
                    <div className="flex items-center gap-2 text-xs font-bold text-blue-300 uppercase tracking-wider mb-2">
                      <span>🎯</span> Próxima Área Inferida pela IA
                    </div>
                    <h3 className="text-base font-bold text-white">
                      {inferenciaSelecionada.proxima_area_inferida}
                    </h3>
                    <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                      {inferenciaSelecionada.motivo_inferencia}
                    </p>

                    <div className="grid grid-cols-2 gap-3 mt-4 pt-4 border-t border-blue-500/20 text-xs">
                      <div>
                        <span className="text-slate-400 text-[11px]">Responsável Previsto:</span>
                        <div className="font-semibold text-white">{inferenciaSelecionada.responsavel_proxima_area}</div>
                      </div>
                      <div>
                        <span className="text-slate-400 text-[11px]">Tempo Estimado:</span>
                        <div className="font-semibold text-emerald-400">{inferenciaSelecionada.tempo_estimado_proxima_etapa}</div>
                      </div>
                    </div>
                  </div>

                  {/* Ação Imediata Recomendada */}
                  <div className="bg-amber-950/20 border border-amber-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-xs font-bold text-amber-400 uppercase tracking-wider mb-1.5">
                      <span>⚡</span> Ação Imediata Recomendada para a Área Atual
                    </div>
                    <p className="text-xs text-slate-200 leading-relaxed font-medium">
                      {inferenciaSelecionada.acao_imediata_recomendada}
                    </p>
                  </div>

                  {/* Checklist de Documentos Necessários */}
                  {inferenciaSelecionada.checklist_documentos_necessarios && (
                    <div className="bg-slate-900 border border-slate-700/80 rounded-xl p-4">
                      <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-2">
                        📋 Checklist de Documentos para Avançar de Fase
                      </span>
                      <ul className="space-y-1.5 text-xs text-slate-300">
                        {inferenciaSelecionada.checklist_documentos_necessarios.map((item, iIdx) => (
                          <li key={iIdx} className="flex items-center gap-2">
                            <span className="text-emerald-400">✓</span> {item}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Caminho Restante Completo */}
                  {inferenciaSelecionada.caminho_restante_completo && (
                    <div className="bg-slate-900 border border-slate-700/80 rounded-xl p-4">
                      <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block mb-3">
                        🗺️ Caminho Lógico Restante até Conclusão
                      </span>
                      <div className="space-y-2.5">
                        {inferenciaSelecionada.caminho_restante_completo.map((step, sIdx) => (
                          <div key={sIdx} className="flex items-center justify-between text-xs p-2.5 bg-slate-800/80 rounded-lg border border-slate-700/60">
                            <div className="flex items-center gap-2">
                              <span className="w-5 h-5 rounded-full bg-blue-600/30 text-blue-300 text-[10px] font-bold flex items-center justify-center">
                                {sIdx + 1}
                              </span>
                              <span className="font-bold text-white">{step.etapa}</span>
                              <span className="text-slate-400">• {step.acao}</span>
                            </div>
                            <span className="text-[11px] text-slate-400 font-mono">SLA: {step.sla_dias}d</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Botão de Documentos SIGA */}
                  <button
                    onClick={() =>
                      setProcessoDocumentosModal({
                        id: inferenciaSelecionada.contrato?.id,
                        numero_processo_siga: inferenciaSelecionada.contrato?.numero_processo_siga,
                        objeto: inferenciaSelecionada.contrato?.objeto
                      })
                    }
                    className="w-full bg-slate-700 hover:bg-slate-600 text-slate-100 font-medium text-xs py-2.5 px-4 rounded-xl border border-slate-600 transition flex items-center justify-center gap-2 shadow"
                  >
                    <span>📎</span> Acessar Documentos e Anexos do Processo SIGA
                  </button>
                </>
              ) : null}
            </div>
          </div>
        </div>
      )}

      {/* ABA 7: ESTEIRA DE GOVERNANÇA DO PLANEJAMENTO PLAC (5 FASES) */}
      {activeSubTab === 'esteira_governanca' && (
        <GovernancaEsteiraKanban />
      )}

      {/* ABA 8: ROBÔ SENTINELA DE PLANEJAMENTO & TELEMETRIA PLAC */}
      {activeSubTab === 'sentinela_planejamento' && (
        <PlanejamentoSentinelaMonitor />
      )}

      {/* Modal de Documentos SIGA Integrado */}
      {processoDocumentosModal && (
        <SigaDocumentsModal
          processo={processoDocumentosModal}
          onClose={() => setProcessoDocumentosModal(null)}
        />
      )}
    </div>
  );
}
