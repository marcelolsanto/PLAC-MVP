import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function ExecutiveDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState('');

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const res = await api.get('/demands/metrics/');
      setMetrics(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  const handleSimulateSync = async () => {
    try {
      setSyncing(true);
      setSyncMessage('');
      const res = await api.post('/demands/simulate_sync/');
      setSyncMessage(res.data.message);
      await fetchMetrics();
    } catch (err) {
      alert('Erro ao disparar simulação de sincronização.');
    } finally {
      setSyncing(false);
    }
  };

  if (loading && !metrics) {
    return <div className="text-center py-12 text-slate-400">Calculando indicadores executivos...</div>;
  }

  const { total_demands, total_budget, tep, iac, pncp_count, contracted_count, priority_distribution } =
    metrics || {
      total_demands: 0,
      total_budget: 0,
      tep: 0,
      iac: 100,
      pncp_count: 0,
      contracted_count: 0,
      priority_distribution: { ALTO: 0, MEDIO: 0, BAIXO: 0 },
    };

  return (
    <div className="space-y-6">
      {/* Cabeçalho do Painel Executivo */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-white">Painel Executivo de Gestão & KPIs (UC04)</h3>
          <p className="text-xs text-slate-400">
            Visão consolidada em tempo real para a Diretoria Executiva — Fim da assimetria de informações
          </p>
        </div>

        <button
          disabled={syncing}
          onClick={handleSimulateSync}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium text-xs rounded-lg shadow transition duration-200 disabled:opacity-50"
        >
          <span>{syncing ? '🔄 Robô Extraindo...' : '⚡ Executar Robô de Automação (Playwright/SIGA)'}</span>
        </button>
      </div>

      {syncMessage && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/40 rounded-lg text-emerald-400 text-xs flex items-center justify-between">
          <span>{syncMessage}</span>
          <span className="font-semibold text-[10px] uppercase tracking-wider bg-emerald-500/20 px-2 py-0.5 rounded">
            Dados Atualizados
          </span>
        </div>
      )}

      {/* Cartões Principais de Indicadores (KPIs) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: TEP */}
        <div className="p-5 bg-slate-800 border border-slate-700 rounded-xl shadow-sm space-y-2">
          <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
            TEP - Taxa de Execução
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-blue-400">{tep}%</span>
            <span className="text-xs text-slate-400">({contracted_count}/{total_demands} contratados)</span>
          </div>
          <p className="text-[11px] text-slate-400">Percentual de demandas com contrato formalizado</p>
        </div>

        {/* KPI 2: IAC */}
        <div className="p-5 bg-slate-800 border border-slate-700 rounded-xl shadow-sm space-y-2">
          <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
            IAC - Aderência ao Calendário
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-emerald-400">{iac}%</span>
          </div>
          <p className="text-[11px] text-slate-400">Processos encaminhados dentro do prazo de SLA legal</p>
        </div>

        {/* KPI 3: Orçamento Total */}
        <div className="p-5 bg-slate-800 border border-slate-700 rounded-xl shadow-sm space-y-2">
          <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
            Volume Orçamentário Total
          </span>
          <div className="text-2xl font-bold text-white truncate">
            R$ {Number(total_budget).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
          </div>
          <p className="text-[11px] text-slate-400">Valor estimado de contratações ativas no PLAC</p>
        </div>

        {/* KPI 4: Integração PNCP */}
        <div className="p-5 bg-slate-800 border border-slate-700 rounded-xl shadow-sm space-y-2">
          <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
            Publicações no PNCP
          </span>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-indigo-400">{pncp_count}</span>
            <span className="text-xs text-slate-400">publicados</span>
          </div>
          <p className="text-[11px] text-slate-400">Sincronizados com o Portal Nacional de Contratações</p>
        </div>
      </div>

      {/* Gráfico de Distribuição por Criticidade / Prioridade */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-sm space-y-4">
        <h4 className="font-bold text-white text-sm">Distribuição das Demandas por Grau de Prioridade (Anexo II)</h4>

        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-red-400 font-semibold">Prioridade Alta (Score ≥ 380)</span>
              <span className="text-slate-300 font-mono">{priority_distribution.ALTO} item(ns)</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-red-500 h-2.5 rounded-full transition-all duration-500"
                style={{
                  width: `${total_demands > 0 ? (priority_distribution.ALTO / total_demands) * 100 : 0}%`,
                }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-amber-400 font-semibold">Prioridade Média (Score 240 a 379)</span>
              <span className="text-slate-300 font-mono">{priority_distribution.MEDIO} item(ns)</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-amber-500 h-2.5 rounded-full transition-all duration-500"
                style={{
                  width: `${total_demands > 0 ? (priority_distribution.MEDIO / total_demands) * 100 : 0}%`,
                }}
              ></div>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-emerald-400 font-semibold">Prioridade Baixa (Score &lt; 240)</span>
              <span className="text-slate-300 font-mono">{priority_distribution.BAIXO} item(ns)</span>
            </div>
            <div className="w-full bg-slate-900 rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-emerald-500 h-2.5 rounded-full transition-all duration-500"
                style={{
                  width: `${total_demands > 0 ? (priority_distribution.BAIXO / total_demands) * 100 : 0}%`,
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
