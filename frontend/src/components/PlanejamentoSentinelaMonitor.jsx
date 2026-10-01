import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function PlanejamentoSentinelaMonitor() {
  const [quadrimestre, setQuadrimestre] = useState('TODOS');
  const [ano, setAno] = useState(2026);
  const [loading, setLoading] = useState(true);
  const [varreduraLoading, setVarreduraLoading] = useState(false);
  const [kpis, setKpis] = useState(null);
  const [ranking, setRanking] = useState([]);
  const [varredura, setVarredura] = useState(null);
  const [feedback, setFeedback] = useState(null);

  const fetchDados = async () => {
    try {
      setLoading(true);
      const params = {};
      if (quadrimestre !== 'TODOS') params.quadrimestre = quadrimestre;
      if (ano) params.ano = ano;

      const [resKpis, resRanking, resVarredura] = await Promise.all([
        api.get('/planejamento/sentinela/kpis/', { params }),
        api.get('/planejamento/sentinela/ranking-areas/', { params: { ano } }),
        api.get('/planejamento/sentinela/varredura/')
      ]);

      setKpis(resKpis.data);
      setRanking(resRanking.data);
      setVarredura(resVarredura.data);
    } catch (err) {
      console.error('Erro ao buscar telemetria do sentinela:', err);
      showFeedback('Erro ao conectar com o Robô Sentinela de Planejamento.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDados();
  }, [quadrimestre, ano]);

  const showFeedback = (msg, type = 'success') => {
    setFeedback({ msg, type });
    setTimeout(() => setFeedback(null), 6000);
  };

  const handleExecutarVarredura = async () => {
    try {
      setVarreduraLoading(true);
      const res = await api.post('/planejamento/sentinela/varredura/');
      setVarredura(res.data);
      showFeedback(
        `Varredura concluída! ${res.data.total_demandas_auditadas} demandas auditadas. ` +
        `${res.data.resumo_alertas.criticos} anomalias críticas encontradas.`
      );
    } catch (err) {
      console.error(err);
      showFeedback('Falha ao executar varredura do sentinela.', 'error');
    } finally {
      setVarreduraLoading(false);
    }
  };

  const formatBRL = (val) => {
    return Number(val || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  return (
    <div className="space-y-6">
      {/* Toast Feedback */}
      {feedback && (
        <div
          className={`p-4 rounded-xl border flex items-center justify-between text-sm shadow-lg transition-all animate-fadeIn ${
            feedback.type === 'error'
              ? 'bg-rose-950/80 border-rose-600/60 text-rose-200'
              : 'bg-emerald-950/80 border-emerald-600/60 text-emerald-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <span>{feedback.type === 'error' ? '⚠️' : '🛡️'}</span>
            <span>{feedback.msg}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-xs opacity-70 hover:opacity-100">✕</button>
        </div>
      )}

      {/* Topo: Painel do Sentinela e Controles */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-xl backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">🤖</span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Robô Sentinela de Planejamento &amp; Telemetria PLAC
              </h2>
              <span className="bg-purple-600/20 text-purple-400 text-xs px-2.5 py-0.5 rounded-full border border-purple-500/30 font-semibold flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                Auditoria Ativa
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Fiscalização contínua de <span className="text-slate-300 font-semibold">IAC, ICNP, TEP e TMP</span> com rastreamento da inércia das áreas demandantes e combate a "urgências fabricadas".
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Seletor de Quadrimestres */}
            <div className="bg-slate-900/90 p-1 rounded-xl border border-slate-700 flex items-center gap-1">
              {[
                { id: 'TODOS', label: 'Todos' },
                { id: 'Q1', label: 'Q1 (Jan-Abr)' },
                { id: 'Q2', label: 'Q2 (Mai-Ago)' },
                { id: 'Q3', label: 'Q3 (Set-Dez)' },
              ].map((q) => (
                <button
                  key={q.id}
                  onClick={() => setQuadrimestre(q.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    quadrimestre === q.id
                      ? 'bg-blue-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  {q.label}
                </button>
              ))}
            </div>

            {/* Botão de Varredura Imediata */}
            <button
              onClick={handleExecutarVarredura}
              disabled={varreduraLoading}
              className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-md transition disabled:opacity-50"
            >
              <span>{varreduraLoading ? '⏳' : '🔍'}</span>
              <span>{varreduraLoading ? 'Auditando...' : 'Varredura Sentinela'}</span>
            </button>
          </div>
        </div>

        {/* 4 Cards com os Indicadores Oficiais de Desempenho Telebras */}
        {kpis && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-700/60">
            {/* KPI 1: IAC */}
            <div className="bg-slate-900/70 border border-slate-700/70 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">IAC - Aderência ao Plano</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    kpis.iac.status === 'CONFORME'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}>
                    {kpis.iac.status === 'CONFORME' ? '🟢 Conforme' : '🔴 Desvio'}
                  </span>
                </div>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-3xl font-extrabold text-white">{kpis.iac.valor}%</span>
                  <span className="text-xs text-slate-400">Meta: &ge; {kpis.iac.meta}%</span>
                </div>
              </div>
              <div className="mt-3">
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-1.5 rounded-full ${kpis.iac.valor >= 85 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                    style={{ width: `${Math.min(100, kpis.iac.valor)}%` }}
                  ></div>
                </div>
                <p className="text-[10px] text-slate-400 mt-1.5">
                  {kpis.iac.demandas_aderentes} de {kpis.iac.total} demandas no prazo
                </p>
              </div>
            </div>

            {/* KPI 2: ICNP */}
            <div className="bg-slate-900/70 border border-slate-700/70 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">ICNP - Fora do Rito</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    kpis.icnp.status === 'CONFORME'
                      ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                      : 'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}>
                    {kpis.icnp.status === 'CONFORME' ? '🟢 Controlado' : '🔴 Urgência Fabricada'}
                  </span>
                </div>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-3xl font-extrabold text-white">{kpis.icnp.valor}%</span>
                  <span className="text-xs text-slate-400">Teto: &le; {kpis.icnp.meta}%</span>
                </div>
              </div>
              <div className="mt-3">
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className={`h-1.5 rounded-full ${kpis.icnp.valor <= 10 ? 'bg-emerald-500' : 'bg-rose-500'}`}
                    style={{ width: `${Math.min(100, kpis.icnp.valor * 2)}%` }}
                  ></div>
                </div>
                <p className="text-[10px] text-slate-400 mt-1.5">
                  {kpis.icnp.demandas_nao_planejadas} urgências detectadas
                </p>
              </div>
            </div>

            {/* KPI 3: TEP */}
            <div className="bg-slate-900/70 border border-slate-700/70 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">TEP - Execução do Plano</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/20 text-blue-400 border border-blue-500/30">
                    Vazão Real
                  </span>
                </div>
                <div className="flex items-baseline gap-2 mt-2">
                  <span className="text-3xl font-extrabold text-white">{kpis.tep.valor}%</span>
                  <span className="text-xs text-slate-400">{kpis.tep.contratadas} / {kpis.tep.total}</span>
                </div>
              </div>
              <div className="mt-3">
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="h-1.5 rounded-full bg-blue-500"
                    style={{ width: `${Math.min(100, kpis.tep.valor)}%` }}
                  ></div>
                </div>
                <p className="text-[10px] text-slate-400 mt-1.5">
                  Contratos publicados no PNCP / vigentes
                </p>
              </div>
            </div>

            {/* KPI 4: TMP (Decomposição Área vs. GCC) */}
            <div className="bg-slate-900/70 border border-slate-700/70 rounded-xl p-4 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">TMP - Decomposição</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                    {kpis.tmp.tempo_medio_global_dias} dias médios
                  </span>
                </div>
                {/* Barra Bicolor de Tempo */}
                <div className="mt-3 space-y-1">
                  <div className="flex items-center justify-between text-[10px] font-semibold">
                    <span className="text-amber-400">Área: {kpis.tmp.dias_area_demandante} d.u. ({kpis.tmp.pct_tempo_area}%)</span>
                    <span className="text-blue-400">GCC: {kpis.tmp.dias_gcc_compras} d.u. ({kpis.tmp.pct_tempo_gcc}%)</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-2 flex overflow-hidden">
                    <div
                      className="bg-amber-500 h-2"
                      style={{ width: `${kpis.tmp.pct_tempo_area}%` }}
                      title={`Área Requisitante: ${kpis.tmp.dias_area_demandante} dias úteis`}
                    ></div>
                    <div
                      className="bg-blue-500 h-2"
                      style={{ width: `${kpis.tmp.pct_tempo_gcc}%` }}
                      title={`GCC Compras: ${kpis.tmp.dias_gcc_compras} dias úteis`}
                    ></div>
                  </div>
                </div>
              </div>
              <p className="text-[9px] text-slate-400 mt-2 italic leading-tight">
                A GCC cumpre os SLAs oficiais; o gargalo principal ocorre na inércia prévia da Área.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Grid Principal: Ranking das Áreas Demandantes + Feed de Alertas do Sentinela */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* LADO ESQUERDO: Ranking de Governança das Áreas (Colunas 1 a 7) */}
        <div className="lg:col-span-7 bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>📊</span> Matriz de Governança das Áreas Demandantes
              </h3>
              <p className="text-[11px] text-slate-400">
                Auditoria de responsabilidade: amarração no SIGA vs. geração de urgências fabricadas.
              </p>
            </div>
            <span className="text-xs font-mono text-slate-400">
              {ranking.length} áreas mapeadas
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[620px]">
              <thead>
                <tr className="border-b border-slate-700/60 text-slate-400 font-semibold uppercase text-[10px]">
                  <th className="py-2 px-2">Área / Gerência</th>
                  <th className="py-2 px-2 text-center">Demandas</th>
                  <th className="py-2 px-2 text-center">Amarração SIGA</th>
                  <th className="py-2 px-2 text-center">Urgências</th>
                  <th className="py-2 px-2 text-center">Score</th>
                  <th className="py-2 px-3 text-center min-w-[170px] whitespace-nowrap">Classificação</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {ranking.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-slate-500 italic">
                      Nenhuma área demandante com registros no período.
                    </td>
                  </tr>
                ) : (
                  ranking.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-750 transition">
                      <td className="py-3 px-2">
                        <div className="font-bold text-white">{item.diretoria}</div>
                        <div className="text-[10px] text-slate-400">{item.gerencia}</div>
                        <div className="text-[10px] text-blue-400 font-semibold">{formatBRL(item.valor_total)}</div>
                      </td>
                      <td className="py-3 px-2 text-center font-bold text-slate-200">
                        {item.total_demandas}
                      </td>
                      <td className="py-3 px-2 text-center">
                        <div className="font-bold text-emerald-400">{item.taxa_siga_pct}%</div>
                        <div className="text-[9px] text-slate-500">{item.com_siga_count} de {item.total_demandas}</div>
                      </td>
                      <td className="py-3 px-2 text-center">
                        {item.urgencias_fabricadas_count > 0 ? (
                          <span className="bg-rose-950/80 border border-rose-800/80 text-rose-300 px-2 py-0.5 rounded font-bold text-[10px]">
                            {item.urgencias_fabricadas_count} alertas
                          </span>
                        ) : (
                          <span className="text-slate-500 text-[10px]">0</span>
                        )}
                      </td>
                      <td className="py-3 px-2 text-center">
                        <div className="inline-flex items-center gap-1.5">
                          <span className="font-extrabold text-white text-sm">{item.score_governanca}</span>
                          <span className="text-[9px] text-slate-500">/100</span>
                        </div>
                      </td>
                      <td className="py-3 px-3 text-center whitespace-nowrap min-w-[170px]">
                        <span className={`inline-flex items-center justify-center whitespace-nowrap text-[11px] font-bold px-3 py-1 rounded-full border shadow-sm ${
                          item.classificacao === 'EXEMPLAR'
                            ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-300'
                            : item.classificacao === 'MODERADO'
                            ? 'bg-amber-500/15 border-amber-500/40 text-amber-300'
                            : 'bg-rose-500/15 border-rose-500/40 text-rose-300'
                        }`}>
                          {item.badge}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* LADO DIREITO: Feed de Alertas Ativos da Varredura (Colunas 8 a 12) */}
        <div className="lg:col-span-5 bg-slate-800/80 border border-slate-700/80 rounded-2xl p-5 shadow-lg space-y-4">
          <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <span>🚨</span> Alertas do Sentinela em Tempo Real
              </h3>
              <p className="text-[11px] text-slate-400">
                Detecção automática de inércia, datas fatais e falsas urgências.
              </p>
            </div>
            {varredura && (
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                varredura.status_geral === 'CRITICO'
                  ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                  : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
              }`}>
                {varredura.resumo_alertas.total_anomalias} anomalias
              </span>
            )}
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[600px] pr-1">
            {!varredura || varredura.alertas.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs italic">
                ✅ Nenhuma inconsistência detectada na esteira do PLAC.
              </div>
            ) : (
              varredura.alertas.map((alt) => (
                <div
                  key={alt.id}
                  className={`p-3.5 rounded-xl border text-xs space-y-2 transition shadow ${
                    alt.severidade === 'CRITICO'
                      ? 'bg-rose-950/40 border-rose-800/60 text-rose-200'
                      : alt.severidade === 'ALERTA'
                      ? 'bg-amber-950/40 border-amber-800/60 text-amber-200'
                      : 'bg-blue-950/40 border-blue-800/60 text-blue-200'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 flex-wrap">
                    <span className="font-mono font-bold text-[10px] bg-slate-900 px-1.5 py-0.5 rounded border border-slate-700">
                      🏷️ {alt.codigo_rastreio}
                    </span>
                    <span className="text-[10px] font-bold uppercase">
                      {alt.severidade_badge}
                    </span>
                  </div>

                  <div>
                    <div className="text-[10px] text-slate-300 font-semibold">{alt.area}</div>
                    <div className="font-medium text-slate-100 mt-0.5">{alt.objeto}</div>
                  </div>

                  <div className="text-[11px] leading-relaxed opacity-90 pt-1 border-t border-slate-700/40">
                    {alt.mensagem}
                  </div>

                  <div className="text-[10px] bg-slate-900/80 p-2 rounded-lg border border-slate-800 text-slate-300">
                    <strong className="text-purple-400">Recomendação Sentinela:</strong> {alt.recomendacao}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
