import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function GCCPanel() {
  const [demands, setDemands] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDemand, setSelectedDemand] = useState(null);
  const [procurementType, setProcurementType] = useState('PREGAO');
  const [actionLoading, setActionLoading] = useState(false);
  const [message, setMessage] = useState('');

  const slaOptions = {
    PREGAO: { label: 'Pregão Eletrônico', days: 157 },
    DISPENSA: { label: 'Dispensa de Licitação', days: 45 },
    INEXIGIBILIDADE: { label: 'Inexigibilidade', days: 60 },
    CONCORRENCIA: { label: 'Concorrência', days: 180 },
  };

  const fetchGCCDemands = async () => {
    try {
      setLoading(true);
      const res = await api.get('/demands/gcc_queue/');
      setDemands(res.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGCCDemands();
  }, []);

  const calculatePreview = (intendedDateStr, type) => {
    if (!intendedDateStr) return null;
    const intended = new Date(intendedDateStr);
    const sla = slaOptions[type]?.days || 157;
    const deadline = new Date(intended.getTime() - sla * 24 * 60 * 60 * 1000);
    const needsAnticipation = deadline.getFullYear() < intended.getFullYear();

    return {
      deadline,
      sla,
      needsAnticipation,
    };
  };

  const handleConsolidate = async () => {
    if (!selectedDemand) return;
    try {
      setActionLoading(true);
      await api.post(`/demands/${selectedDemand.id}/consolidate/`, {
        procurement_type: procurementType,
      });
      setMessage(`Demanda #${selectedDemand.id} consolidada no Calendário com SLA de ${slaOptions[procurementType].days} dias e enviada à DAFRI!`);
      setSelectedDemand(null);
      fetchGCCDemands();
    } catch (err) {
      alert('Erro ao consolidar processo.');
    } finally {
      setActionLoading(false);
    }
  };

  const preview = selectedDemand ? calculatePreview(selectedDemand.intended_date, procurementType) : null;

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-xl font-bold text-white">Consolidação e Calendário Automático (UC03)</h3>
        <p className="text-xs text-slate-400">
          Gerência de Compras e Contratos (GCC) - Estabelecer modalidade, SLA e datas-limite
        </p>
      </div>

      {message && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/40 rounded-lg text-emerald-400 text-sm">
          {message}
        </div>
      )}

      {loading ? (
        <div className="text-center py-10 text-slate-400">Carregando fila da GCC...</div>
      ) : demands.length === 0 ? (
        <div className="p-8 text-center bg-slate-800 border border-slate-700 rounded-xl text-slate-400">
          Nenhuma demanda aguardando consolidação da GCC no momento.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {demands.map((demand) => (
            <div
              key={demand.id}
              className="p-4 bg-slate-800 border border-slate-700 rounded-xl hover:border-slate-600 transition flex items-center justify-between"
            >
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-mono bg-slate-900 text-slate-300 px-2 py-0.5 rounded">
                    #{demand.id}
                  </span>
                  <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 font-semibold">
                    Validado pelo Diretor
                  </span>
                </div>
                <h4 className="text-white font-medium">{demand.description}</h4>
                <p className="text-xs text-slate-400">
                  Data de Assinatura Pretendida:{' '}
                  <strong className="text-slate-300">
                    {new Date(demand.intended_date).toLocaleDateString('pt-BR')}
                  </strong>{' '}
                  | Valor: R$ {Number(demand.estimated_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </p>
              </div>

              <button
                onClick={() => setSelectedDemand(demand)}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition shadow"
              >
                Gerar Calendário & SLA
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Modal de Definição de SLA e Calendário */}
      {selectedDemand && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center p-4 z-50">
          <div className="bg-slate-800 border border-slate-700 max-w-xl w-full rounded-xl p-6 space-y-5 text-white">
            <div className="flex items-center justify-between pb-3 border-b border-slate-700">
              <h3 className="font-bold text-lg">Definir Forma de Contratação & SLA</h3>
              <button
                onClick={() => setSelectedDemand(null)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="p-3 bg-slate-900/60 rounded-lg text-sm space-y-1">
              <p className="text-slate-200 font-medium">{selectedDemand.description}</p>
              <p className="text-xs text-slate-400">
                Data Pretendida de Assinatura:{' '}
                <strong className="text-white">
                  {new Date(selectedDemand.intended_date).toLocaleDateString('pt-BR')}
                </strong>
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1">
                Forma de Contratação (Regra de SLA)
              </label>
              <select
                value={procurementType}
                onChange={(e) => setProcurementType(e.target.value)}
                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {Object.entries(slaOptions).map(([key, item]) => (
                  <option key={key} value={key}>
                    {item.label} (SLA: {item.days} dias)
                  </option>
                ))}
              </select>
            </div>

            {/* Painel do Calendário Calculado */}
            {preview && (
              <div className="p-4 bg-slate-900/80 border border-slate-700 rounded-xl space-y-3">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-400">Prazo de Subtração de SLA:</span>
                  <span className="font-bold text-blue-400">{preview.sla} dias</span>
                </div>

                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-400">Data-Limite de Encaminhamento:</span>
                  <span className="font-bold text-white text-base">
                    {preview.deadline.toLocaleDateString('pt-BR')}
                  </span>
                </div>

                {/* Alerta Visual de Antecipação (Fluxo Alternativo UC03) */}
                {preview.needsAnticipation && (
                  <div className="p-3 bg-red-500/15 border border-red-500/60 rounded-lg text-xs text-red-300 flex items-start gap-2">
                    <span className="text-red-400 font-bold text-sm leading-none">⚠️</span>
                    <div>
                      <strong className="block text-red-400 font-semibold mb-0.5">
                        Alerta de Antecipação (Ano Anterior)
                      </strong>
                      A data-limite calculada ({preview.deadline.getFullYear()}) recai no ano anterior ao da contratação pretendida ({new Date(selectedDemand.intended_date).getFullYear()}). É obrigatório antecipar a instrução do processo imediatamente!
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-3 border-t border-slate-700">
              <button
                onClick={() => setSelectedDemand(null)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded text-sm transition"
              >
                Cancelar
              </button>
              <button
                disabled={actionLoading}
                onClick={handleConsolidate}
                className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition shadow"
              >
                {actionLoading ? 'Processando...' : 'Encaminhar Proposta à DAFRI'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
