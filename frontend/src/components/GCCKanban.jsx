import React, { useState, useEffect } from 'react';
import api from '../services/api';
import AIDraftingModal from './AIDraftingModal';

const columns = [
  { id: 'nova', title: 'Novas Demandas (Entrada)', color: 'bg-slate-700/50', border: 'border-slate-600', icon: '📥' },
  { id: 'planejamento', title: 'Planejamento (ETP/TR)', color: 'bg-blue-900/30', border: 'border-blue-700', icon: '📝' },
  { id: 'juridico', title: 'Análise Jurídica', color: 'bg-purple-900/30', border: 'border-purple-700', icon: '⚖️' },
  { id: 'licitacao', title: 'Licitação / PNCP', color: 'bg-amber-900/30', border: 'border-amber-700', icon: '📢' },
  { id: 'contrato', title: 'Homologação & Contrato', color: 'bg-emerald-900/30', border: 'border-emerald-700', icon: '✅' },
];

export default function GCCKanban() {
  const [demands, setDemands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [aiModalDemand, setAiModalDemand] = useState(null);

  useEffect(() => {
    fetchDemands();
  }, []);

  const fetchDemands = async () => {
    try {
      // Fetch data and distribute across columns to simulate flow
      const res = await api.get('/demands/');
      const data = res.data.map((d, index) => ({
        ...d,
        // Mock distribution just for this prototype
        column: columns[index % columns.length].id,
      }));
      setDemands(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            📊 Kanban de Gestão Operacional (Execução)
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Visualização estratégica do ciclo de vida das contratações. (Prova de Conceito Baseada nas Planilhas de Fluxo)
          </p>
        </div>
        <div className="flex gap-2">
          <button className="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 transition">
            Filtros Avançados
          </button>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10 text-slate-400">Carregando painel operacional...</div>
      ) : (
        <div className="flex gap-4 overflow-x-auto pb-4 hide-scrollbar">
          {columns.map((col) => (
            <div key={col.id} className="flex-none w-80 flex flex-col h-[calc(100vh-220px)]">
              {/* Column Header */}
              <div className={`p-3 rounded-t-lg border-t border-x ${col.border} ${col.color} flex items-center justify-between`}>
                <h4 className="font-semibold text-sm text-slate-200 flex items-center gap-1.5">
                  <span>{col.icon}</span>
                  {col.title}
                </h4>
                <span className="text-xs font-bold text-slate-400 bg-slate-900/50 px-2 py-0.5 rounded-full">
                  {demands.filter(d => d.column === col.id).length}
                </span>
              </div>
              
              {/* Column Body */}
              <div className={`flex-1 p-2 bg-slate-800/30 border-x border-b rounded-b-lg ${col.border} overflow-y-auto space-y-3`}>
                {demands.filter(d => d.column === col.id).map(demand => (
                  <div key={demand.id} className="p-3 bg-slate-800 border border-slate-700 hover:border-blue-500/50 rounded-lg shadow-sm cursor-grab active:cursor-grabbing transition group">
                    <div className="flex items-start justify-between mb-2">
                      <span className="text-[10px] font-mono bg-slate-900 text-slate-400 px-1.5 py-0.5 rounded">
                        #{demand.id}
                      </span>
                      <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-slate-700 text-slate-300">
                        {demand.procurement_type || 'A Definir'}
                      </span>
                    </div>
                    
                    <p className="text-sm text-slate-200 font-medium leading-snug mb-3 line-clamp-2" title={demand.description}>
                      {demand.description}
                    </p>
                    
                    <div className="flex items-center justify-between mt-auto">
                      <div className="text-[10px] text-slate-400 font-medium bg-slate-900 px-1.5 py-0.5 rounded border border-slate-700">
                        💰 R$ {Number(demand.estimated_value).toLocaleString('pt-BR', { notation: 'compact' })}
                      </div>
                      <div className="text-[10px] text-slate-400 flex items-center gap-1">
                        ⏳ SLA: {demand.sla_days || 157}d
                      </div>
                    </div>

                    {/* Fake Progress bar based on column */}
                    <div className="mt-3 w-full bg-slate-900 rounded-full h-1.5 overflow-hidden mb-3">
                      <div 
                        className={`h-full ${col.id === 'nova' ? 'w-10 bg-slate-500' : col.id === 'planejamento' ? 'w-1/4 bg-blue-500' : col.id === 'juridico' ? 'w-2/4 bg-purple-500' : col.id === 'licitacao' ? 'w-3/4 bg-amber-500' : 'w-full bg-emerald-500'}`}
                      ></div>
                    </div>

                    <button
                      onClick={() => setAiModalDemand(demand)}
                      className="w-full py-1.5 bg-indigo-600/10 hover:bg-indigo-600/30 text-indigo-400 border border-indigo-500/20 text-[10px] font-bold rounded transition text-center"
                    >
                      ✨ IA Copilot (ETP/TR)
                    </button>
                  </div>
                ))}
                
                {demands.filter(d => d.column === col.id).length === 0 && (
                  <div className="text-center p-4 text-xs text-slate-500 border border-dashed border-slate-700 rounded-lg">
                    Nenhuma demanda
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
      {aiModalDemand && (
        <AIDraftingModal demand={aiModalDemand} onClose={() => setAiModalDemand(null)} />
      )}
    </div>
  );
}
