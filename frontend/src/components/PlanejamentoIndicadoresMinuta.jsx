import React, { useState, useEffect } from 'react';

export default function PlanejamentoIndicadoresMinuta() {
  const [indicadores, setIndicadores] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quadrimestre, setQuadrimestre] = useState('anual');

  // Estado para consulta de preços no PNCP (IN 65/2021)
  const [termoPncp, setTermoPncp] = useState('');
  const [resultadoPncp, setResultadoPncp] = useState(null);
  const [loadingPncp, setLoadingPncp] = useState(false);

  useEffect(() => {
    fetchIndicadores();
  }, [quadrimestre]);

  const fetchIndicadores = async () => {
    setLoading(true);
    try {
      const res = await fetch(`http://localhost:8000/api/planejamento/indicadores-minuta/?quadrimestre=${quadrimestre}`);
      if (res.ok) {
        const data = await res.json();
        setIndicadores(data);
      }
    } catch (err) {
      console.error("Erro ao buscar indicadores da Minuta:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleConsultarPncp = async (e) => {
    e.preventDefault();
    if (!termoPncp.trim()) return;
    setLoadingPncp(true);
    try {
      const res = await fetch(`http://localhost:8000/api/planejamento/pncp-precos/?termo=${encodeURIComponent(termoPncp)}`);
      if (res.ok) {
        const data = await res.json();
        setResultadoPncp(data);
      }
    } catch (err) {
      console.error("Erro ao consultar PNCP:", err);
    } finally {
      setLoadingPncp(false);
    }
  };

  const getStatusBadge = (status, cor) => {
    if (cor === 'emerald') {
      return <span className="px-2.5 py-1 text-xs font-bold rounded-md bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">🟢 {status}</span>;
    }
    if (cor === 'amber') {
      return <span className="px-2.5 py-1 text-xs font-bold rounded-md bg-amber-500/20 text-amber-300 border border-amber-500/40">🟡 {status}</span>;
    }
    return <span className="px-2.5 py-1 text-xs font-bold rounded-md bg-rose-500/20 text-rose-300 border border-rose-500/40">🔴 {status}</span>;
  };

  return (
    <div className="space-y-6">
      {/* Cabeçalho Executivo */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl -z-10" />
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xl">📜</span>
              <span className="text-xs font-bold text-blue-400 uppercase tracking-widest">
                Governança Oficial Telebras • Art. 47 &amp; Anexo IV da Minuta PLAC
              </span>
            </div>
            <h1 className="text-2xl font-black text-white tracking-tight">
              Indicadores Oficiais de Desempenho do PLAC
            </h1>
            <p className="text-xs text-slate-400 mt-1 max-w-3xl leading-relaxed">
              Painel quadrimestral obrigatório de aferição de eficácia do planejamento (TEP), aderência ao calendário de envio à GCC (IAC), índice de imprevistos (ICNP) e estabilidade do plano (IAP), em cumprimento ao RELIC e à Resolução CGPAR nº 45/2022.
            </p>
          </div>

          {/* Seletor de Período Regimental */}
          <div className="flex items-center gap-2 bg-slate-950 p-1.5 rounded-xl border border-slate-800 shrink-0">
            <span className="text-[11px] font-semibold text-slate-400 px-2">Período:</span>
            {[
              { id: '1Q', label: '1º Q (Abril)' },
              { id: '2Q', label: '2º Q (Agosto)' },
              { id: '3Q', label: '3º Q (Dezembro)' },
              { id: 'anual', label: 'Consolidado Anual' }
            ].map(tab => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setQuadrimestre(tab.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition ${
                  quadrimestre === tab.id
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'text-slate-400 hover:text-white hover:bg-slate-850'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Grid dos 5 Indicadores Primários (Anexo IV) */}
      {loading ? (
        <div className="text-center py-16 text-slate-400">Carregando telemetria regimental da Minuta...</div>
      ) : indicadores ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* 1. TEP */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition flex flex-col justify-between shadow-lg">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-blue-400 font-mono">I. TEP</span>
                  {getStatusBadge(indicadores.tep.status, indicadores.tep.cor)}
                </div>
                <div className="text-3xl font-black text-white mt-3 font-mono">
                  {indicadores.tep.valor}%
                </div>
                <div className="text-xs font-bold text-slate-200 mt-1">
                  Taxa de Execução do PLAC
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">
                  {indicadores.tep.concluidas} de {indicadores.tep.planejadas} contratações concluídas no período.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Meta Regimental:</span>
                <span className="font-bold text-emerald-400">{indicadores.tep.meta}</span>
              </div>
            </div>

            {/* 2. IAC */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition flex flex-col justify-between shadow-lg">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-blue-400 font-mono">II. IAC</span>
                  {getStatusBadge(indicadores.iac.status, indicadores.iac.cor)}
                </div>
                <div className="text-3xl font-black text-white mt-3 font-mono">
                  {indicadores.iac.valor}%
                </div>
                <div className="text-xs font-bold text-slate-200 mt-1">
                  Aderência ao Calendário
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">
                  {indicadores.iac.encaminhados_no_prazo} de {indicadores.iac.total_encaminhados} processos enviados à GCC no prazo regimental.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Meta Regimental:</span>
                <span className="font-bold text-emerald-400">{indicadores.iac.meta}</span>
              </div>
            </div>

            {/* 3. ICNP */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition flex flex-col justify-between shadow-lg">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-blue-400 font-mono">III. ICNP</span>
                  {getStatusBadge(indicadores.icnp.status, indicadores.icnp.cor)}
                </div>
                <div className="text-3xl font-black text-white mt-3 font-mono">
                  {indicadores.icnp.valor}%
                </div>
                <div className="text-xs font-bold text-slate-200 mt-1">
                  Contratações Não Planejadas
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">
                  {indicadores.icnp.itens_incluidos} demandas incluídas no curso do exercício (Art. 34/41).
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Limite Máximo:</span>
                <span className="font-bold text-emerald-400">{indicadores.icnp.meta}</span>
              </div>
            </div>

            {/* 4. IAP */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition flex flex-col justify-between shadow-lg">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-blue-400 font-mono">IV. IAP</span>
                  {getStatusBadge(indicadores.iap.status, indicadores.iap.cor)}
                </div>
                <div className="text-3xl font-black text-white mt-3 font-mono">
                  {indicadores.iap.valor}%
                </div>
                <div className="text-xs font-bold text-slate-200 mt-1">
                  Índice de Alterações
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">
                  {indicadores.iap.alteracoes} alterações de escopo, prazo ou valor aprovadas no ciclo.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Limite Máximo:</span>
                <span className="font-bold text-emerald-400">{indicadores.iap.meta}</span>
              </div>
            </div>

            {/* 5. TMP */}
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition flex flex-col justify-between shadow-lg">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-blue-400 font-mono">V. TMP</span>
                  <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">Anexo III</span>
                </div>
                <div className="text-3xl font-black text-white mt-3 font-mono">
                  {indicadores.tmp.valor_dias_uteis}d
                </div>
                <div className="text-xs font-bold text-slate-200 mt-1">
                  Tempo Médio de Processamento
                </div>
                <p className="text-[11px] text-slate-400 mt-1.5 leading-snug">
                  Aproximadamente {indicadores.tmp.meses_aprox} meses úteis da entrada na GCC até a contratação.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-400">
                <span>Amostra Real:</span>
                <span className="font-bold text-indigo-300">{indicadores.tmp.concluidas_amostra} processos</span>
              </div>
            </div>
          </div>

          {/* Painel Inferior Duplo: Saneamento & Diligências + Marcos Regimentais */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Bloco 1: Indicadores Complementares de Saneamento (Art. 40 §1º) */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-lg">⚖️</span>
                <h3 className="text-sm font-extrabold text-white">
                  Controle de Devoluções &amp; Saneamento (Art. 40)
                </h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Mede o retrabalho decorrente de processos encaminhados com instrução incompleta pelas áreas requisitantes.
              </p>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                  <span className="text-[11px] text-slate-400 block font-semibold">Taxa de Devolução</span>
                  <span className="text-2xl font-black text-amber-400 font-mono mt-1 block">
                    {indicadores.complementares.taxa_devolucao_instrucao_incompleta}%
                  </span>
                  <span className="text-[10px] text-slate-400 mt-0.5 block">
                    ({indicadores.complementares.devolucoes_total} processos devolvidos)
                  </span>
                </div>
                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                  <span className="text-[11px] text-slate-400 block font-semibold">Tempo de Saneamento</span>
                  <span className="text-2xl font-black text-rose-400 font-mono mt-1 block">
                    {indicadores.complementares.tempo_medio_saneamento_dias}d
                  </span>
                  <span className="text-[10px] text-slate-400 mt-0.5 block">
                    dias úteis médios para ajuste
                  </span>
                </div>
              </div>

              <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-[11px] text-amber-300 leading-relaxed">
                ⚠️ Conforme o § 1º do art. 40, processos devolvidos suspendem a contagem do calendário e devem constar no Relatório Gerencial da GCC.
              </div>
            </div>

            {/* Bloco 2: Cronograma Operacional Anual (Art. 15 da Minuta) */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4">
              <div className="flex items-center gap-2">
                <span className="text-lg">🗓️</span>
                <h3 className="text-sm font-extrabold text-white">
                  Cronograma Operacional do Ciclo (Art. 15)
                </h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Marcos regimentais obrigatórios para a elaboração e aprovação do PLAC pela Diretoria Executiva.
              </p>

              <div className="space-y-2.5 pt-1 text-xs">
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-300">1. Divulgação do Cronograma GCC:</span>
                  <span className="font-mono font-bold text-blue-400">Até 30/06</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-300">2. Encerramento dos Registros:</span>
                  <span className="font-mono font-bold text-amber-400">Até 31/07</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-300">3. Envio da Proposta à DAFRI:</span>
                  <span className="font-mono font-bold text-indigo-400">Até 15/10</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                  <span className="text-slate-300">4. Manifestação Conclusiva DAFRI:</span>
                  <span className="font-mono font-bold text-purple-400">1ª Quinzena Nov</span>
                </div>
                <div className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-emerald-500/30 bg-emerald-500/5">
                  <span className="text-white font-bold">5. Aprovação em Ata REDIR:</span>
                  <span className="font-mono font-black text-emerald-400">Até 30/11</span>
                </div>
              </div>
            </div>

            {/* Bloco 3: Assistente de Precificação PNCP (IN 65/2021) */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-4 flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">🔍</span>
                  <h3 className="text-sm font-extrabold text-white">
                    Pesquisa de Preços Pública (PNCP / IN 65)
                  </h3>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Consulte referências homologadas recentes na base nacional para instrução rápida do ETP e TR.
                </p>

                <form onSubmit={handleConsultarPncp} className="flex gap-2">
                  <input
                    type="text"
                    value={termoPncp}
                    onChange={(e) => setTermoPncp(e.target.value)}
                    placeholder="Ex: DWDM, Servidor Rack, Firewall..."
                    className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500"
                  />
                  <button
                    type="submit"
                    disabled={loadingPncp}
                    className="px-3.5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl transition shrink-0"
                  >
                    {loadingPncp ? '...' : 'Buscar'}
                  </button>
                </form>

                {resultadoPncp && (
                  <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 space-y-2 text-xs">
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>Média Homologada:</span>
                      <span className="font-mono font-bold text-emerald-400">
                        R$ {resultadoPncp.estatisticas.media_preco.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400">
                      <span>Mínimo / Máximo:</span>
                      <span className="font-mono text-slate-300">
                        R$ {resultadoPncp.estatisticas.minimo_preco.toLocaleString('pt-BR')} / R$ {resultadoPncp.estatisticas.maximo_preco.toLocaleString('pt-BR')}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-400 border-t border-slate-800 pt-1.5 flex items-center justify-between">
                      <span>{resultadoPncp.estatisticas.total_amostras} compras encontradas</span>
                      <span className="text-blue-400 font-semibold">Fonte: PNCP Oficial</span>
                    </div>
                  </div>
                )}
              </div>

              <div className="text-[10px] text-slate-400 pt-2 border-t border-slate-800">
                Atende ao Art. 21, IV da Minuta e aos critérios da IN SGD/ME nº 65/2021.
              </div>
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
