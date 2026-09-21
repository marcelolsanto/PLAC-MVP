import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function DirectorApprovalPanel() {
  const [pendingDemands, setPendingDemands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDemand, setSelectedDemand] = useState(null);
  const [rejectReason, setRejectReason] = useState('');
  const [isRejecting, setIsRejecting] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [message, setMessage] = useState('');

  const fetchPending = async () => {
    try {
      setLoading(true);
      const res = await api.get('/demands/pending_approvals/');
      setPendingDemands(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  const handleApprove = async (id) => {
    try {
      setActionLoading(true);
      await api.post(`/demands/${id}/approve/`);
      setMessage('Demanda validada e encaminhada com sucesso para a fila da GCC!');
      setSelectedDemand(null);
      fetchPending();
    } catch (err) {
      alert('Erro ao aprovar demanda.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (id) => {
    if (!rejectReason.trim()) {
      alert('Por favor, informe o motivo da devolução para ajustes.');
      return;
    }
    try {
      setActionLoading(true);
      await api.post(`/demands/${id}/reject/`, { reason: rejectReason });
      setMessage('Demanda devolvida para ajustes com o motivo registrado.');
      setSelectedDemand(null);
      setIsRejecting(false);
      setRejectReason('');
      fetchPending();
    } catch (err) {
      alert('Erro ao devolver demanda.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white">Painel de Deliberação Estratégica (UC02)</h3>
        <p className="text-xs text-slate-400">
          Avaliação de conveniência, aderência orçamentária e priorização das áreas subordinadas
        </p>
      </div>

      {message && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/40 rounded-lg text-emerald-400 text-sm">
          {message}
        </div>
      )}

      {loading ? (
        <div className="text-center py-10 text-slate-400">Carregando fila de aprovação...</div>
      ) : pendingDemands.length === 0 ? (
        <div className="p-8 text-center bg-slate-800 border border-slate-700 rounded-xl text-slate-400">
          Nenhuma demanda pendente de validação no momento.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {pendingDemands.map((demand) => (
            <div
              key={demand.id}
              className="p-4 bg-slate-800 border border-slate-700 rounded-xl hover:border-slate-600 transition flex items-center justify-between"
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono bg-slate-900 text-slate-300 px-2 py-0.5 rounded">
                    #{demand.id}
                  </span>
                  <span className="text-xs text-slate-400 font-semibold uppercase">{demand.item_type}</span>
                  <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded border border-blue-500/30">
                    Prioridade: {demand.priority_level} ({demand.priority_score} pts)
                  </span>
                </div>
                <h4 className="text-white font-medium">{demand.description}</h4>
                <p className="text-xs text-slate-400">
                  Solicitante: <strong className="text-slate-300">{demand.created_by_name}</strong> | Valor: R${' '}
                  {Number(demand.estimated_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>

              <button
                onClick={() => {
                  setSelectedDemand(demand);
                  setIsRejecting(false);
                  setRejectReason('');
                }}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 text-sm font-medium rounded-lg transition"
              >
                Revisar e Deliberar
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Modal de Análise do Diretor */}
      {selectedDemand && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 border border-slate-700 max-w-2xl w-full rounded-xl p-6 space-y-5 text-white">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700">
              <h3 className="font-bold text-lg">Revisão de Demanda #{selectedDemand.id}</h3>
              <button
                onClick={() => setSelectedDemand(null)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm bg-slate-900/60 p-4 rounded-lg">
              <div>
                <span className="text-slate-400 block text-xs">Objeto:</span>
                <p className="font-medium text-slate-200">{selectedDemand.description}</p>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Valor Estimado:</span>
                <p className="font-medium text-slate-200">
                  R$ {Number(selectedDemand.estimated_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Catálogo CATMAT:</span>
                <p className="font-medium text-slate-200">{selectedDemand.catmat_code}</p>
              </div>
              <div>
                <span className="text-slate-400 block text-xs">Pretensão de Assinatura:</span>
                <p className="font-medium text-slate-200">
                  {new Date(selectedDemand.intended_date).toLocaleDateString('pt-BR')}
                </p>
              </div>
              <div className="col-span-2">
                <span className="text-slate-400 block text-xs">Vinculação Estratégica:</span>
                <p className="font-medium text-slate-200">{selectedDemand.strategic_alignment}</p>
              </div>
            </div>

            {/* Avaliação das Notas */}
            <div className="p-3 bg-slate-900/40 border border-slate-700/60 rounded-lg text-xs space-y-1">
              <p className="font-semibold text-slate-300">Resumo dos Fatores de Priorização:</p>
              <div className="grid grid-cols-4 gap-2 text-slate-400">
                <div>F1 (Criticidade): <strong className="text-white">{selectedDemand.f1}</strong></div>
                <div>F2 (Urgência): <strong className="text-white">{selectedDemand.f2}</strong></div>
                <div>F3 (Impacto): <strong className="text-white">{selectedDemand.f3}</strong></div>
                <div>F4 (Materialidade): <strong className="text-white">{selectedDemand.f4}</strong></div>
              </div>
              <p className="text-blue-400 pt-1">
                Fórmula: ({selectedDemand.f1}×30) + ({selectedDemand.f2}×30) + ({selectedDemand.f3}×25) + ({selectedDemand.f4}×15) = <strong>{selectedDemand.priority_score} pts ({selectedDemand.priority_level})</strong>
              </p>
            </div>

            {/* Ações ou Campo de Devolução */}
            {isRejecting ? (
              <div className="space-y-3 pt-2">
                <label className="block text-xs font-semibold text-red-400">
                  Motivo da Devolução para Ajustes (Obrigatório):
                </label>
                <textarea
                  rows="3"
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Explique detalhadamente o ajuste necessário..."
                  className="w-full px-3 py-2 bg-slate-900 border border-red-500/50 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                />
                <div className="flex justify-end gap-2">
                  <button
                    onClick={() => setIsRejecting(false)}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm transition"
                  >
                    Voltar
                  </button>
                  <button
                    disabled={actionLoading}
                    onClick={() => handleReject(selectedDemand.id)}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded text-sm transition"
                  >
                    {actionLoading ? 'Processando...' : 'Confirmar Devolução'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-700">
                <button
                  onClick={() => setIsRejecting(true)}
                  className="px-4 py-2 bg-amber-600/20 text-amber-300 border border-amber-500/40 hover:bg-amber-600/30 text-sm font-medium rounded-lg transition"
                >
                  Devolver para Ajustes
                </button>
                <button
                  disabled={actionLoading}
                  onClick={() => handleApprove(selectedDemand.id)}
                  className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition shadow"
                >
                  {actionLoading ? 'Processando...' : '✓ Validar Demanda'}
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
