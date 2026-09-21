import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function ExecutiveDeliberationPanel() {
  const [demands, setDemands] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useAuth();
  
  // States for REDIR approval
  const [minuteNumber, setMinuteNumber] = useState('');
  const [isApproving, setIsApproving] = useState(false);

  // States for DAFRI modal
  const [selectedDemandDafri, setSelectedDemandDafri] = useState(null);
  const [dafriOpinion, setDafriOpinion] = useState('');
  const [dafriApproved, setDafriApproved] = useState(true);
  
  // States for REDIR reject modal
  const [selectedDemandReject, setSelectedDemandReject] = useState(null);
  const [rejectReason, setRejectReason] = useState('');

  const fetchQueue = async () => {
    try {
      setLoading(true);
      const res = await api.get('/demands/dafri_queue/');
      setDemands(res.data);
    } catch (err) {
      console.error('Erro ao buscar fila de deliberação', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const handleDafriSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/demands/${selectedDemandDafri.id}/dafri_opinion/`, {
        opinion: dafriOpinion,
        approved: dafriApproved
      });
      setSelectedDemandDafri(null);
      setDafriOpinion('');
      setDafriApproved(true);
      fetchQueue();
    } catch (err) {
      alert('Erro ao registrar parecer: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleRedirApproveAll = async () => {
    if (!minuteNumber.trim()) {
      alert('Informe o número da Ata da REDIR.');
      return;
    }
    if (!confirm('Tem certeza que deseja aprovar o PLAC e virar o ciclo para VIGENTE?')) return;
    
    try {
      setIsApproving(true);
      const res = await api.post('/demands/redir_approve/', {
        minute_number: minuteNumber
      });
      alert(res.data.message);
      setMinuteNumber('');
      fetchQueue();
    } catch (err) {
      alert('Erro ao aprovar PLAC: ' + (err.response?.data?.error || err.message));
    } finally {
      setIsApproving(false);
    }
  };

  const handleRedirReject = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/demands/${selectedDemandReject.id}/redir_reject/`, {
        reason: rejectReason
      });
      setSelectedDemandReject(null);
      setRejectReason('');
      fetchQueue();
    } catch (err) {
      alert('Erro ao reprovar demanda: ' + (err.response?.data?.error || err.message));
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
        <h2 className="text-lg font-bold text-white mb-2">Painel de Reunião de Diretoria (REDIR)</h2>
        <p className="text-sm text-slate-400 mb-4">
          A aprovação do plano consolidado efetiva todas as demandas da fila para o status VIGENTE.
        </p>
        
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-xs font-medium text-slate-400 mb-1">
              Número da Ata da REDIR
            </label>
            <input
              type="text"
              className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm"
              placeholder="Ex: Ata REDIR Nº 45/2026"
              value={minuteNumber}
              onChange={(e) => setMinuteNumber(e.target.value)}
            />
          </div>
          <button
            onClick={handleRedirApproveAll}
            disabled={isApproving || demands.length === 0}
            className="bg-emerald-600 hover:bg-emerald-500 text-white font-medium py-2 px-6 rounded transition disabled:opacity-50"
          >
            {isApproving ? 'Processando...' : 'Aprovar PLAC Anual (Tornar Vigente)'}
          </button>
        </div>
      </div>

      <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
        <div className="p-4 border-b border-slate-700">
          <h3 className="font-semibold text-white">Fila de Demandas (Consolidadas)</h3>
        </div>
        
        {loading ? (
          <div className="p-8 text-center text-slate-400">Carregando itens para deliberação...</div>
        ) : demands.length === 0 ? (
          <div className="p-8 text-center text-slate-400">Nenhuma demanda consolidada aguardando deliberação.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/50 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-4 py-3">Objeto</th>
                  <th className="px-4 py-3">Valor Est.</th>
                  <th className="px-4 py-3">SLA / Limite</th>
                  <th className="px-4 py-3">Parecer DAFRI</th>
                  <th className="px-4 py-3 text-right">Ações REDIR</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {demands.map(d => (
                  <tr key={d.id} className="hover:bg-slate-750">
                    <td className="px-4 py-3">
                      <div className="font-medium text-slate-200">{d.description}</div>
                      <div className="text-xs text-slate-500">{d.procurement_type}</div>
                    </td>
                    <td className="px-4 py-3">
                      R$ {parseFloat(d.estimated_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-xs">{d.sla_days} dias</div>
                      <div className="text-xs text-slate-400">{d.submission_deadline}</div>
                    </td>
                    <td className="px-4 py-3">
                      {d.dafri_opinion ? (
                        <div className="text-xs">
                          <span className={d.dafri_approved ? 'text-emerald-400' : 'text-red-400'}>
                            {d.dafri_approved ? '✓ Favorável' : '✗ Desfavorável'}
                          </span>
                          <div className="text-slate-400 truncate max-w-xs" title={d.dafri_opinion}>
                            {d.dafri_opinion}
                          </div>
                        </div>
                      ) : (
                        <button
                          onClick={() => setSelectedDemandDafri(d)}
                          className="text-xs bg-blue-600/20 text-blue-400 px-2 py-1 rounded hover:bg-blue-600/40"
                        >
                          Emitir Parecer
                        </button>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => setSelectedDemandReject(d)}
                        className="text-xs bg-red-900/40 text-red-400 px-2 py-1 rounded hover:bg-red-800/60"
                      >
                        Reprovar Item
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal DAFRI */}
      {selectedDemandDafri && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-lg w-full border border-slate-600 shadow-xl">
            <h3 className="text-lg font-bold text-white mb-4">Emitir Parecer DAFRI</h3>
            <p className="text-sm text-slate-300 mb-4">{selectedDemandDafri.description}</p>
            
            <form onSubmit={handleDafriSubmit}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">
                    Parecer Técnico (Adequação Orçamentária)
                  </label>
                  <textarea
                    className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm h-24"
                    value={dafriOpinion}
                    onChange={(e) => setDafriOpinion(e.target.value)}
                    required
                  ></textarea>
                </div>
                <div>
                  <label className="flex items-center space-x-2 text-sm text-slate-300">
                    <input
                      type="checkbox"
                      className="rounded bg-slate-900 border-slate-700 text-blue-500"
                      checked={dafriApproved}
                      onChange={(e) => setDafriApproved(e.target.checked)}
                    />
                    <span>Parecer Favorável (Aprovado)</span>
                  </label>
                </div>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedDemandDafri(null)}
                  className="px-4 py-2 text-sm text-slate-300 hover:text-white"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded text-sm font-medium"
                >
                  Salvar Parecer
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal Reprovação REDIR */}
      {selectedDemandReject && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 rounded-lg p-6 max-w-lg w-full border border-slate-600 shadow-xl">
            <h3 className="text-lg font-bold text-white mb-4">Reprovar Demanda na REDIR</h3>
            <p className="text-sm text-slate-300 mb-4">A demanda será devolvida à GCC/Área com o motivo registrado.</p>
            
            <form onSubmit={handleRedirReject}>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">
                  Motivo da Reprovação (Ata)
                </label>
                <textarea
                  className="w-full bg-slate-900 border border-slate-700 rounded p-2 text-white text-sm h-24"
                  value={rejectReason}
                  onChange={(e) => setRejectReason(e.target.value)}
                  placeholder="Ex: Item não contemplado no orçamento anual aprovado."
                  required
                ></textarea>
              </div>
              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setSelectedDemandReject(null)}
                  className="px-4 py-2 text-sm text-slate-300 hover:text-white"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="bg-red-600 hover:bg-red-500 text-white px-4 py-2 rounded text-sm font-medium"
                >
                  Devolver Demanda
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
