import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function PlanejamentoEsteiraKanban() {
  const [ano, setAno] = useState(2026);
  const [diretoria, setDiretoria] = useState('TODAS');
  const [risco, setRisco] = useState('TODOS');
  const [busca, setBusca] = useState('');
  const [loading, setLoading] = useState(true);
  
  // Dados recebidos do backend
  const [kpis, setKpis] = useState(null);
  const [colunasConfig, setColunasConfig] = useState([]);
  const [colunas, setColunas] = useState({
    '1_DFD': [],
    '2_ETP': [],
    '3_PESQUISA_TR': [],
    '4_JURIDICO': [],
    '5_GCC': []
  });

  // Modal de Detalhes do Processo
  const [selectedProcess, setSelectedProcess] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const fetchKanbanTelemetria = async () => {
    try {
      setLoading(true);
      const params = { ano };
      if (diretoria !== 'TODAS') params.diretoria = diretoria;
      if (risco !== 'TODOS') params.risco = risco;
      if (busca.trim()) params.busca = busca.trim();

      const res = await api.get('/planejamento/kanban-telemetria/', { params });
      setKpis(res.data.kpis);
      setColunasConfig(res.data.colunas_config || []);
      setColunas(res.data.colunas || {});
    } catch (err) {
      console.error('Erro ao carregar telemetria kanban:', err);
      showFeedback('Erro ao carregar telemetria do Kanban de planejamento.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKanbanTelemetria();
  }, [ano, diretoria, risco]);

  // Debounce na busca textual
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchKanbanTelemetria();
    }, 350);
    return () => clearTimeout(timer);
  }, [busca]);

  const showFeedback = (msg, type = 'success') => {
    setFeedback({ msg, type });
    setTimeout(() => setFeedback(null), 5000);
  };

  const formatCurrency = (val) => {
    if (!val && val !== 0) return 'R$ 0,00';
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(val);
  };

  return (
    <div className="p-4 sm:p-6 space-y-6 max-w-[1700px] mx-auto animate-fadeIn text-slate-100">
      {/* Toast Feedback */}
      {feedback && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-xl shadow-2xl border text-sm font-semibold flex items-center gap-2 animate-bounce ${
            feedback.type === 'error'
              ? 'bg-rose-950/90 border-rose-500 text-rose-200'
              : 'bg-emerald-950/90 border-emerald-500 text-emerald-200'
          }`}
        >
          <span>{feedback.type === 'error' ? '❌' : '✅'}</span>
          <span>{feedback.msg}</span>
        </div>
      )}

      {/* Cabeçalho Executivo */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-700/80 rounded-2xl p-5 shadow-xl">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-2xl">📡</span>
              <h1 className="text-xl sm:text-2xl font-black text-white tracking-tight">
                Esteira Kanban da Fase de Planejamento (SIGA {ano})
              </h1>
              <span className="bg-blue-600/30 text-blue-300 border border-blue-500/40 text-[11px] font-bold px-2.5 py-0.5 rounded-full">
                186 Processos Ativos
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-4xl leading-relaxed">
              Mapeamento em tempo real de todos os processos em tramitação preparatória interna no SIGA para contratação ainda em 2026.
              Monitoramento de setores, custodiantes, desvio em relação à média e prevenção ativa de apagão orçamentário.
            </p>
          </div>

          {/* Botões de Ação e Acesso aos Entregáveis */}
          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              onClick={fetchKanbanTelemetria}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-lg border border-slate-600 transition shadow-sm"
              title="Recarregar esteira"
            >
              <span>🔄</span>
              <span>Atualizar</span>
            </button>
            <a
              href="file:///Z:/PLAC-MVP/RELATORIO_EXECUTIVO_PLANEJAMENTO_KANBAN_SIGA_2026.pdf"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-rose-950/80 hover:bg-rose-900 text-rose-200 border border-rose-600/60 rounded-lg text-xs font-bold transition shadow-sm"
            >
              <span>📄</span>
              <span>Relatório PDF (3 págs)</span>
            </a>
            <a
              href="file:///Z:/PLAC-MVP/BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026.xlsx"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-950/80 hover:bg-emerald-900 text-emerald-200 border border-emerald-600/60 rounded-lg text-xs font-bold transition shadow-sm"
            >
              <span>📊</span>
              <span>Planilha Excel (4 abas)</span>
            </a>
          </div>
        </div>

        {/* 5 Cartões Superiores de Telemetria (KPIs) */}
        {kpis && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 mt-5">
            <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-3">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                Carteira de Planejamento
              </span>
              <div className="text-xl font-black text-white mt-1">
                {kpis.total_processos} processos
              </div>
              <span className="text-[10px] text-blue-400 font-semibold block mt-0.5">
                {formatCurrency(kpis.valor_total_rs)} em trânsito
              </span>
            </div>

            <div className="bg-slate-800/80 border border-amber-500/30 rounded-xl p-3">
              <span className="text-[10px] font-bold text-amber-300 uppercase tracking-wider block">
                Maior Gargalo: ETP &amp; Riscos
              </span>
              <div className="text-xl font-black text-amber-400 mt-1">
                {colunas['2_ETP']?.length || 0} processos
              </div>
              <span className="text-[10px] text-slate-400 font-medium block mt-0.5">
                Média: 37,8 dias no setor (SLA 35d)
              </span>
            </div>

            <div className="bg-slate-800/80 border border-rose-500/30 rounded-xl p-3">
              <span className="text-[10px] font-bold text-rose-300 uppercase tracking-wider block">
                Gargalos Críticos (&gt;10d)
              </span>
              <div className="text-xl font-black text-rose-400 mt-1">
                {kpis.gargalos_criticos} processos
              </div>
              <span className="text-[10px] text-rose-300/80 font-medium block mt-0.5">
                Desvio grave além do SLA
              </span>
            </div>

            <div className="bg-slate-800/80 border border-red-600/40 rounded-xl p-3 bg-red-950/20">
              <span className="text-[10px] font-bold text-red-300 uppercase tracking-wider block">
                Risco de Não Contratar 2026
              </span>
              <div className="text-xl font-black text-red-400 mt-1 flex items-center gap-1.5">
                <span>🔥</span>
                <span>{kpis.risco_apagao_2026} demandas</span>
              </div>
              <span className="text-[10px] text-red-200 font-medium block mt-0.5">
                Restam &lt; 60 dias úteis p/ licitar
              </span>
            </div>

            <div className="bg-slate-800/80 border border-slate-700 rounded-xl p-3">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                Tempo Médio de Retenção
              </span>
              <div className="text-xl font-black text-slate-200 mt-1">
                {kpis.tempo_medio_global_dias} dias úteis
              </div>
              <span className="text-[10px] text-emerald-400 font-semibold block mt-0.5">
                Média global entre etapas
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Barra de Filtros Interativos */}
      <div className="bg-slate-850 border border-slate-750 p-3.5 rounded-xl shadow flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          {/* Seletor de Diretoria */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-bold text-slate-400">Diretoria:</span>
            <select
              value={diretoria}
              onChange={(e) => setDiretoria(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-white text-xs rounded-lg px-2.5 py-1.5 font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            >
              <option value="TODAS">Todas as Diretorias</option>
              <option value="3000">3000 - DTO (Técnico-Operacional)</option>
              <option value="2000">2000 - DAFRI (Administrativo-Financeira)</option>
              <option value="4000">4000 - DC (Comercial)</option>
              <option value="1000">1000 - PR (Presidência)</option>
              <option value="5000">5000 - DGOV (Governança)</option>
            </select>
          </div>

          {/* Seletor de Criticidade/Risco */}
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-bold text-slate-400">Criticidade:</span>
            <select
              value={risco}
              onChange={(e) => setRisco(e.target.value)}
              className="bg-slate-900 border border-slate-700 text-white text-xs rounded-lg px-2.5 py-1.5 font-medium focus:ring-1 focus:ring-blue-500 outline-none"
            >
              <option value="TODOS">Todos os Prazos</option>
              <option value="CRITICOS">🚨 Apenas Gargalos Críticos (&gt;10d)</option>
              <option value="RISCO_2026">🔥 Risco de Não Contratar em 2026</option>
              <option value="ATENCAO">⚠️ Em Atenção (&gt;0d)</option>
            </select>
          </div>
        </div>

        {/* Campo de Busca Rápida */}
        <div className="relative w-full md:w-80">
          <input
            type="text"
            placeholder="Buscar processo, objeto, setor ou responsável..."
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
          <span className="absolute left-2.5 top-2 text-slate-500 text-xs">🔍</span>
          {busca && (
            <button
              onClick={() => setBusca('')}
              className="absolute right-2.5 top-1.5 text-slate-400 hover:text-white text-xs"
            >
              ✕
            </button>
          )}
        </div>
      </div>

      {/* Grid Principal: As 5 Colunas da Esteira Kanban */}
      {loading ? (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-16 text-center space-y-3">
          <div className="inline-block animate-spin text-3xl">⚙️</div>
          <div className="text-sm font-bold text-slate-300">
            Sincronizando telemetria dos 186 processos no SIGA...
          </div>
          <p className="text-xs text-slate-500">
            Calculando médias históricas, desvios e viabilidade de contratação em 2026.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-5 gap-4 items-start">
          {colunasConfig.map((colCfg) => {
            const itensColuna = colunas[colCfg.id] || [];
            return (
              <div
                key={colCfg.id}
                className={`bg-slate-900/90 border border-slate-800 rounded-2xl flex flex-col shadow-lg overflow-hidden ${colCfg.cor_header}`}
              >
                {/* Cabeçalho da Coluna */}
                <div className="p-3.5 bg-slate-850 border-b border-slate-800 flex flex-col gap-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-black text-white tracking-tight">
                      {colCfg.titulo}
                    </h3>
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${colCfg.cor_badge}`}>
                      {itensColuna.length}
                    </span>
                  </div>
                  <div className="text-[10px] text-slate-400 flex items-center justify-between mt-0.5">
                    <span>{colCfg.subtitulo}</span>
                    <span className="font-semibold text-slate-300">
                      {formatCurrency(colCfg.valor_total)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[9px] text-slate-500 pt-1 border-t border-slate-800/60 mt-1">
                    <span>SLA: {colCfg.sla_etapa}d úteis</span>
                    <span>Média Real: {colCfg.media_historica}d</span>
                  </div>
                </div>

                {/* Lista de Cards da Coluna */}
                <div className="p-2.5 space-y-2.5 max-h-[750px] overflow-y-auto pr-1">
                  {itensColuna.length === 0 ? (
                    <div className="text-center py-10 px-2 text-slate-500 text-xs italic">
                      Nenhum processo nesta etapa com os filtros selecionados.
                    </div>
                  ) : (
                    itensColuna.map((proc) => {
                      const isCritico = proc.status_prazo_badge === 'CRITICO';
                      const isAtencao = proc.status_prazo_badge === 'ATENCAO';
                      const isRiscoApagao = proc.risco_nivel === 'ALTO';

                      return (
                        <div
                          key={proc.id}
                          className={`bg-slate-800/90 hover:bg-slate-750 border transition-all rounded-xl p-3 shadow-md flex flex-col gap-2 relative ${
                            isCritico
                              ? 'border-rose-500/80 shadow-rose-950/20'
                              : isAtencao
                              ? 'border-amber-500/60 shadow-amber-950/10'
                              : 'border-slate-700/80'
                          }`}
                        >
                          {/* Topo do Card: Processo SIGA + Origem PLAC + Prioridade */}
                          <div className="flex items-start justify-between gap-1.5">
                            <div>
                              <span className="text-xs font-mono font-black text-blue-300 block">
                                {proc.numero_processo_siga}
                              </span>
                              <span className="text-[9px] font-bold text-slate-400">
                                {proc.cod_verif}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span
                                className={`text-[8.5px] font-bold px-1.5 py-0.5 rounded border ${
                                  proc.origem_plac === 'EXTRAORDINÁRIO'
                                    ? 'bg-rose-950/80 text-rose-300 border-rose-600/50'
                                    : proc.origem_plac.includes('2025')
                                    ? 'bg-amber-950/80 text-amber-300 border-amber-600/50'
                                    : 'bg-blue-950/80 text-blue-300 border-blue-600/50'
                                }`}
                              >
                                {proc.origem_plac === 'EXTRAORDINÁRIO' ? '⚠️ Extraordinário (Art. 34/41)' : `${proc.origem_plac} (Art. 39)`}
                              </span>
                              <span
                                className={`text-[8.5px] font-bold px-1.5 py-0.5 rounded ${
                                  proc.prioridade === 'ALTA'
                                    ? 'bg-rose-950 text-rose-300'
                                    : 'bg-slate-700 text-slate-300'
                                }`}
                              >
                                {proc.prioridade === 'ALTA' ? 'Prioridade ALTA (1º Q)' : proc.prioridade}
                              </span>
                            </div>
                          </div>

                          {/* Objeto e Valor */}
                          <div>
                            <p className="text-[11px] font-medium text-slate-200 line-clamp-2 leading-snug">
                              {proc.objeto}
                            </p>
                            <div className="text-xs font-black text-emerald-400 mt-1">
                              {formatCurrency(proc.valor_estimado_2026)}
                            </div>
                          </div>

                          {/* Localização e Custódia (Onde está e com quem está) */}
                          <div className="bg-slate-850/90 rounded-lg p-2 border border-slate-750 text-[10px] space-y-1">
                            <div className="flex items-center gap-1.5 text-slate-300">
                              <span title="Lotação Atual">🏢</span>
                              <span className="font-bold text-indigo-300">
                                {proc.setor_atual_sigla}
                              </span>
                              <span className="text-slate-400 truncate">
                                — {proc.setor_atual_nome.split('-')[1] || proc.setor_atual_nome}
                              </span>
                            </div>
                            <div className="flex items-center gap-1.5 text-slate-300">
                              <span title="Responsável / Custodiante">👤</span>
                              <span className="font-semibold text-slate-200 truncate">
                                {proc.custodiante_atual}
                              </span>
                            </div>
                          </div>

                          {/* Status da Ação em Andamento */}
                          <div className="text-[10px] text-slate-400 flex items-start gap-1">
                            <span className="text-xs">⚙️</span>
                            <span className="line-clamp-2 leading-tight">
                              <b>Ação:</b> {proc.acao_em_andamento}
                            </span>
                          </div>

                          {/* Telemetria Temporal & Desvio da Média */}
                          <div className="space-y-1 pt-1 border-t border-slate-750/80">
                            <div className="flex items-center justify-between text-[10px]">
                              <span className="text-slate-400 font-medium">
                                Tempo no Setor:
                              </span>
                              <span
                                className={`font-mono font-bold ${
                                  isCritico
                                    ? 'text-rose-400'
                                    : isAtencao
                                    ? 'text-amber-400'
                                    : 'text-emerald-400'
                                }`}
                              >
                                {proc.dias_no_setor} dias (SLA: {proc.sla_etapa}d)
                              </span>
                            </div>

                            {/* Badge Diferença em Relação à Média */}
                            <div
                              className={`text-[9.5px] px-2 py-1 rounded font-semibold flex items-center justify-between ${
                                proc.desvio_media > 0
                                  ? 'bg-rose-950/60 text-rose-300 border border-rose-800/40'
                                  : 'bg-emerald-950/60 text-emerald-300 border border-emerald-800/40'
                              }`}
                            >
                              <span>{proc.desvio_media > 0 ? '⚠️' : '✅'} Comparado à Média:</span>
                              <span className="font-bold">{proc.diff_media_str}</span>
                            </div>
                          </div>

                          {/* Alerta de Risco para 2026 */}
                          {isRiscoApagao && (
                            <div className="bg-red-950/80 border border-red-500/60 rounded-lg p-1.5 text-[9.5px] text-red-200 flex items-start gap-1 animate-pulse font-bold">
                              <span>🔥</span>
                              <span className="leading-tight">
                                Risco Alto: Restam &lt; 60 dias úteis para certame em 2026.
                              </span>
                            </div>
                          )}

                          {/* Documentos Produzidos & Próxima Peça Obrigatória */}
                          <div className="text-[9.5px] space-y-1">
                            <div className="flex flex-wrap gap-1">
                              {proc.documentos_produzidos.slice(0, 3).map((docName, i) => (
                                <span
                                  key={i}
                                  className="bg-slate-700/60 text-slate-300 px-1.5 py-0.5 rounded text-[8.5px] border border-slate-650"
                                >
                                  ✓ {docName.split('-')[0].trim()}
                                </span>
                              ))}
                            </div>
                            <div className="text-[9px] text-amber-300 font-semibold truncate">
                              🛑 <b>Pendente:</b> {proc.proximo_documento_pendente}
                            </div>
                          </div>

                          {/* Botão para Abrir Dossiê Completo */}
                          <button
                            type="button"
                            onClick={() => setSelectedProcess(proc)}
                            className="mt-1 w-full py-1.5 bg-slate-700/70 hover:bg-blue-600 text-slate-200 hover:text-white rounded-lg text-[10px] font-bold transition flex items-center justify-center gap-1 shadow-sm"
                          >
                            <span>🔍</span>
                            <span>Ver Histórico no SIGA</span>
                          </button>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Modal de Detalhes e Dossiê do Processo */}
      {selectedProcess && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl animate-scaleIn text-slate-100 flex flex-col max-h-[90vh]">
            {/* Topo do Modal */}
            <div className="bg-slate-850 p-4 border-b border-slate-700 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">📁</span>
                <div>
                  <h3 className="text-base font-black text-white">
                    Dossiê do Processo: {selectedProcess.numero_processo_siga}
                  </h3>
                  <span className="text-xs text-slate-400">
                    {selectedProcess.cod_verif} | {selectedProcess.origem_plac} | {selectedProcess.diretoria}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedProcess(null)}
                className="text-slate-400 hover:text-white text-lg font-bold p-1"
              >
                ✕
              </button>
            </div>

            {/* Conteúdo do Modal */}
            <div className="p-5 overflow-y-auto space-y-4 text-xs">
              {/* Objeto Completo */}
              <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700 space-y-1">
                <span className="font-bold text-slate-400 uppercase tracking-wider text-[10px]">
                  Objeto da Contratação
                </span>
                <p className="text-sm font-medium text-slate-200 leading-relaxed">
                  {selectedProcess.objeto}
                </p>
                <div className="flex items-center justify-between pt-2 border-t border-slate-700/60 mt-2">
                  <span className="text-slate-400">Valor Estimado:</span>
                  <span className="text-base font-black text-emerald-400">
                    {formatCurrency(selectedProcess.valor_estimado_2026)}
                  </span>
                </div>
              </div>

              {/* Informações de Localização, Custódia e Prazos */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
                <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-750">
                  <span className="text-[10px] text-slate-400 block">Lotação Atual</span>
                  <span className="font-bold text-white text-xs mt-0.5 block">
                    {selectedProcess.setor_atual_sigla}
                  </span>
                  <span className="text-[9px] text-slate-400 truncate block">
                    {selectedProcess.setor_atual_nome}
                  </span>
                </div>

                <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-750">
                  <span className="text-[10px] text-slate-400 block">Custodiante</span>
                  <span className="font-bold text-white text-xs mt-0.5 block truncate">
                    {selectedProcess.custodiante_atual}
                  </span>
                  <span className="text-[9px] text-indigo-300 block">
                    Responsável pelos autos
                  </span>
                </div>

                <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-750">
                  <span className="text-[10px] text-slate-400 block">Permanência</span>
                  <span className="font-bold text-rose-300 text-xs mt-0.5 block">
                    {selectedProcess.dias_no_setor} dias úteis
                  </span>
                  <span className="text-[9px] text-slate-400 block">
                    SLA: {selectedProcess.sla_etapa}d | Média: {selectedProcess.media_etapa}d
                  </span>
                </div>

                <div className="bg-slate-800/60 p-2.5 rounded-lg border border-slate-750">
                  <span className="text-[10px] text-slate-400 block">Risco Exercício 2026</span>
                  <span
                    className={`font-black text-xs mt-0.5 block ${
                      selectedProcess.risco_nivel === 'ALTO'
                        ? 'text-red-400'
                        : selectedProcess.risco_nivel === 'MEDIO'
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }`}
                  >
                    {selectedProcess.risco_nivel}
                  </span>
                  <span className="text-[9px] text-slate-400 block truncate">
                    Viabilidade de licitar
                  </span>
                </div>
              </div>

              {/* Linha do Tempo de Tramitação no SIGA */}
              <div className="space-y-2">
                <span className="font-bold text-slate-300 text-xs flex items-center gap-1.5">
                  <span>📜</span> Histórico Completo de Tramitações e Despachos no SIGA
                </span>
                <div className="border-l-2 border-blue-500/40 ml-2 pl-4 space-y-3">
                  {selectedProcess.timeline_tramitacao.map((item, idx) => (
                    <div key={idx} className="relative group">
                      <div className="absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full bg-blue-500 ring-4 ring-slate-900" />
                      <div className="bg-slate-800/70 p-2.5 rounded-lg border border-slate-750 space-y-1">
                        <div className="flex items-center justify-between text-[10px] text-slate-400">
                          <span className="font-bold text-blue-300">{item.setor}</span>
                          <span className="font-mono">{item.data}</span>
                        </div>
                        <p className="text-slate-200 text-xs leading-snug">
                          {item.despacho}
                        </p>
                        <div className="text-[9px] text-slate-400 flex items-center gap-1 pt-1 border-t border-slate-700/40">
                          <span>👤 Servidor:</span>
                          <span className="font-medium text-slate-300">{item.servidor}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Peças Juntadas e Próximo Passo */}
              <div className="bg-slate-800/60 p-3 rounded-xl border border-slate-750 space-y-2">
                <div className="font-bold text-slate-300 text-xs flex items-center gap-1.5">
                  <span>📎</span> Documentos Produzidos no Processo Eletrônico
                </div>
                <div className="flex flex-wrap gap-1.5">
                  {selectedProcess.documentos_produzidos.map((doc, idx) => (
                    <span
                      key={idx}
                      className="bg-slate-700 px-2 py-1 rounded text-slate-200 text-[10px] font-medium border border-slate-600"
                    >
                      📄 {doc}
                    </span>
                  ))}
                </div>
                <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-medium">Próxima Peça Obrigatória:</span>
                  <span className="font-bold text-amber-300 bg-amber-950/60 px-2 py-0.5 rounded border border-amber-500/40">
                    {selectedProcess.proximo_documento_pendente}
                  </span>
                </div>
              </div>
            </div>

            {/* Rodapé do Modal */}
            <div className="p-3 bg-slate-850 border-t border-slate-700 flex items-center justify-between">
              <span className="text-[10px] text-slate-400">
                Modelo de Contratação: <b>{selectedProcess.modelo_contratacao}</b>
              </span>
              <button
                type="button"
                onClick={() => setSelectedProcess(null)}
                className="px-4 py-1.5 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-xs font-bold transition"
              >
                Fechar Dossiê
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
