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

  const { 
    total_demands, total_budget, tep, iac, icnp, iap, tmp, pncp_count, contracted_count, priority_distribution, monthly_execution 
  } = metrics || {
    total_demands: 0, total_budget: 0, tep: 0, iac: 100, icnp: 0, iap: 0, tmp: 0, pncp_count: 0, contracted_count: 0, 
    priority_distribution: { ALTO: 0, MEDIO: 0, BAIXO: 0 }, monthly_execution: []
  };

  const getMaxExecution = () => Math.max(...(monthly_execution || []).map(m => Math.max(m.planejado, m.executado)), 1);
  const maxExecution = getMaxExecution();

  return (
    <div className="space-y-6">
      {/* Cabeçalho do Painel Executivo */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            📊 Painel de Controle de Execução (KPIs da Diretriz)
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Visão consolidada do PLAC conforme regras oficiais (Art. 34 e Índices de Desempenho)
          </p>
        </div>

        <div className="flex gap-2">
          <select className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded px-3 py-2">
            <option>1º Quadrimestre / 2026</option>
            <option>2º Quadrimestre / 2026</option>
            <option>3º Quadrimestre / 2026</option>
          </select>
          <button
            disabled={syncing}
            onClick={handleSimulateSync}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium text-xs rounded-lg shadow transition duration-200 disabled:opacity-50"
          >
            <span>{syncing ? '🤖 Extraindo...' : '🔁 Atualizar Base SIGA/PNCP'}</span>
          </button>
        </div>
      </div>

      {syncMessage && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/40 rounded-lg text-emerald-400 text-xs flex items-center justify-between">
          <span>{syncMessage}</span>
          <span className="font-semibold text-[10px] uppercase tracking-wider bg-emerald-500/20 px-2 py-0.5 rounded">
            Atualizado
          </span>
        </div>
      )}

      {/* Cartões Principais de Indicadores (KPIs Oficiais da Diretriz) */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {/* KPI 1: TEP */}
        <div className="p-4 bg-slate-800 border border-slate-700 rounded-xl shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition text-4xl">📈</div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-bold block mb-1">
            TEP (Taxa de Execução)
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-extrabold text-blue-400">{tep}%</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1 leading-tight">Itens assinados vs Pretendidos no período</p>
        </div>

        {/* KPI 2: IAC */}
        <div className="p-4 bg-slate-800 border border-slate-700 rounded-xl shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition text-4xl">📅</div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-bold block mb-1">
            IAC (Aderência Calendário)
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-extrabold text-emerald-400">{iac}%</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1 leading-tight">Processos na GCC no prazo do SLA</p>
        </div>

        {/* KPI 3: ICNP */}
        <div className="p-4 bg-slate-800 border border-slate-700 rounded-xl shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition text-4xl">⚠️</div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-bold block mb-1">
            ICNP (Não Previstas)
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-extrabold text-amber-400">{icnp}%</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1 leading-tight">Demanda extraordinária (Art. 34)</p>
        </div>

        {/* KPI 4: IAP */}
        <div className="p-4 bg-slate-800 border border-slate-700 rounded-xl shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition text-4xl">🔄</div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-bold block mb-1">
            IAP (Alteração do Plano)
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-extrabold text-indigo-400">{iap}%</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1 leading-tight">Alterações aprovadas via REDIR</p>
        </div>

        {/* KPI 5: TMP */}
        <div className="p-4 bg-slate-800 border border-slate-700 rounded-xl shadow-sm relative overflow-hidden group">
          <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:opacity-20 transition text-4xl">⏱️</div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wider font-bold block mb-1">
            TMP (Tempo Médio)
          </span>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-extrabold text-purple-400">{tmp}</span>
            <span className="text-xs text-slate-400">dias</span>
          </div>
          <p className="text-[10px] text-slate-500 mt-1 leading-tight">Média entre entrada GCC e assinatura</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Gráfico TEP vs Mensal (Visualização com Tailwind) */}
        <div className="lg:col-span-2 bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm space-y-4">
          <h4 className="font-bold text-white text-sm">Volume Executado vs Planejado (Curva S)</h4>
          <div className="h-48 flex items-end justify-between gap-2 pt-4">
            {(monthly_execution || []).map((m) => (
              <div key={m.name} className="flex-1 flex flex-col justify-end items-center gap-1 group relative">
                {/* Barras */}
                <div className="w-full flex justify-center gap-1 items-end h-full">
                  <div 
                    className="w-1/3 bg-slate-600 rounded-t-sm hover:bg-slate-500 transition-all"
                    style={{ height: `${(m.planejado / maxExecution) * 100}%` }}
                    title={`Planejado: ${m.planejado}`}
                  ></div>
                  <div 
                    className="w-1/3 bg-blue-500 rounded-t-sm hover:bg-blue-400 transition-all"
                    style={{ height: `${(m.executado / maxExecution) * 100}%` }}
                    title={`Executado: ${m.executado}`}
                  ></div>
                </div>
                <span className="text-[10px] text-slate-400 font-medium">{m.name}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-center gap-4 text-[10px] text-slate-400 mt-2">
            <div className="flex items-center gap-1"><span className="w-2 h-2 bg-slate-600 rounded-full"></span> Planejado</div>
            <div className="flex items-center gap-1"><span className="w-2 h-2 bg-blue-500 rounded-full"></span> Executado (TEP)</div>
          </div>
        </div>

        {/* Orçamento e Prioridades */}
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow-sm flex flex-col justify-between space-y-4">
          <div>
            <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
              Volume Orçamentário Total
            </span>
            <div className="text-3xl font-bold text-white truncate mt-1">
              R$ {Number(total_budget).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-[11px] text-slate-400">Soma de contratações ativas no PLAC</p>
          </div>

          <div className="space-y-3 pt-4 border-t border-slate-700/50">
            <h4 className="font-bold text-white text-xs">Distribuição por Prioridade</h4>
            <div>
              <div className="flex justify-between text-[10px] mb-1">
                <span className="text-red-400 font-semibold">Alta (Score 380)</span>
                <span className="text-slate-300 font-mono">{priority_distribution.ALTO} item(ns)</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                <div className="bg-red-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${total_demands > 0 ? (priority_distribution.ALTO / total_demands) * 100 : 0}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[10px] mb-1">
                <span className="text-amber-400 font-semibold">Média (Score 240 a 379)</span>
                <span className="text-slate-300 font-mono">{priority_distribution.MEDIO} item(ns)</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                <div className="bg-amber-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${total_demands > 0 ? (priority_distribution.MEDIO / total_demands) * 100 : 0}%` }}></div>
              </div>
            </div>
            <div>
              <div className="flex justify-between text-[10px] mb-1">
                <span className="text-emerald-400 font-semibold">Baixa (Score &lt; 240)</span>
                <span className="text-slate-300 font-mono">{priority_distribution.BAIXO} item(ns)</span>
              </div>
              <div className="w-full bg-slate-900 rounded-full h-1.5 overflow-hidden">
                <div className="bg-emerald-500 h-1.5 rounded-full transition-all duration-500" style={{ width: `${total_demands > 0 ? (priority_distribution.BAIXO / total_demands) * 100 : 0}%` }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
