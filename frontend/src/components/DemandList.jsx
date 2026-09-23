import React, { useState } from 'react';
import AIDraftingModal from './AIDraftingModal';

export default function DemandList({ demands, onNewDemandClick, onEditDemandClick }) {
  const [aiModalDemand, setAiModalDemand] = useState(null);
  const getPriorityBadge = (level, score) => {
    switch (level) {
      case 'ALTO':
        return (
          <span className="bg-red-500/20 text-red-400 border border-red-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">
            Prioridade Alta ({score} pts)
          </span>
        );
      case 'MEDIO':
        return (
          <span className="bg-amber-500/20 text-amber-400 border border-amber-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">
            Prioridade Média ({score} pts)
          </span>
        );
      case 'BAIXO':
      default:
        return (
          <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">
            Prioridade Baixa ({score} pts)
          </span>
        );
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'AGUARDANDO_VALIDACAO':
        return (
          <span className="bg-blue-500/10 text-blue-400 border border-blue-500/30 text-xs px-2 py-0.5 rounded">
            Aguardando validação superior
          </span>
        );
      case 'VALIDADO_DIRETOR':
        return (
          <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs px-2 py-0.5 rounded font-medium">
            ✓ Validado pela Diretoria (Fila GCC)
          </span>
        );
      case 'DEVOLVIDO_AJUSTES':
        return (
          <span className="bg-red-500/10 text-red-400 border border-red-500/30 text-xs px-2 py-0.5 rounded font-medium">
            Devolvido para Ajustes
          </span>
        );
      default:
        return <span className="text-slate-400 text-xs">{status}</span>;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white">Necessidades Registradas</h3>
          <p className="text-xs text-slate-400">Esteira operacional das demandas de contratação</p>
        </div>
        <button
          onClick={onNewDemandClick}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow transition"
        >
          + Nova Necessidade
        </button>
      </div>

      {demands.length === 0 ? (
        <div className="p-8 text-center bg-slate-800 border border-slate-700 rounded-xl text-slate-400">
          Nenhuma demanda registrada até o momento. Clique em "+ Nova Necessidade" para criar a primeira.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {demands.map((demand) => (
            <div
              key={demand.id}
              className={`p-4 bg-slate-800 border ${
                demand.status === 'DEVOLVIDO_AJUSTES' ? 'border-red-500/50' : 'border-slate-700'
              } rounded-xl hover:border-slate-600 transition shadow-sm space-y-3`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono bg-slate-900 text-slate-300 px-2 py-0.5 rounded">
                      #{demand.id}
                    </span>
                    <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                      {demand.item_type}
                    </span>
                    {getPriorityBadge(demand.priority_level, demand.priority_score)}
                  </div>
                  <h4 className="text-white font-medium text-base pt-1">{demand.description}</h4>
                  <p className="text-xs text-slate-400">
                    Catálogo: <strong className="text-slate-300">{demand.catmat_code}</strong> | Vinculação:{' '}
                    {demand.strategic_alignment}
                  </p>
                </div>

                <div className="text-right space-y-1">
                  <p className="text-white font-semibold text-sm">
                    R$ {Number(demand.estimated_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </p>
                  <p className="text-xs text-slate-400">
                    Pretensão: {new Date(demand.intended_date).toLocaleDateString('pt-BR')}
                  </p>
                                    <div className="pt-1 flex items-center gap-2">
                    {getStatusBadge(demand.status)}
                    <button
                      onClick={() => setAiModalDemand(demand)}
                      className="px-2 py-1 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 text-[10px] font-bold rounded-md transition"
                    >
                      ✨ Assistente IA (ETP/TR)
                    </button>
                  </div>
                </div>
              </div>

              {/* Destaque do motivo se foi devolvido e botão para editar */}
              {demand.status === 'DEVOLVIDO_AJUSTES' && (
                <div className="space-y-2">
                  {demand.rejection_reason && (
                    <div className="p-3 bg-red-950/40 border border-red-500/30 rounded-lg text-xs text-red-300 flex items-start gap-2">
                      <span className="font-bold text-red-400 shrink-0">Motivo da Devolução:</span>
                      <span>{demand.rejection_reason}</span>
                    </div>
                  )}
                  <div className="flex justify-end pt-1">
                    <button
                      onClick={() => onEditDemandClick && onEditDemandClick(demand)}
                      className="px-4 py-2 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-700 hover:to-amber-700 text-white font-semibold text-xs rounded-lg transition shadow flex items-center gap-1.5"
                    >
                      <span>✏️</span>
                      <span>Ajustar Proposta e Reenviar</span>
                    </button>
                  </div>
                </div>
              )}
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
