import React, { useState } from 'react';
import api from '../services/api';
import CatmatAutocomplete from '../components/CatmatAutocomplete';

export default function NewDemand({ onDemandCreated, onCancel, demandToEdit }) {
  const isEditing = Boolean(demandToEdit);

  const [formData, setFormData] = useState({
    // Bloco 1
    directorate: demandToEdit?.directorate || '',
    management_unit: demandToEdit?.management_unit || '',
    responsible_name: demandToEdit?.responsible_name || '',
    responsible_email: demandToEdit?.responsible_email || '',
    nature_type: demandToEdit?.nature_type || 'NOVA',
    // Bloco 2
    description: demandToEdit?.description || '',
    item_type: demandToEdit?.item_type || 'BEM',
    catmat_code: demandToEdit?.catmat_code || '',
    quantity: demandToEdit?.quantity || 1,
    unit: demandToEdit?.unit || '',
    justification: demandToEdit?.justification || '',
    strategic_alignment: demandToEdit?.strategic_alignment || '',
    // Bloco 3
    current_contract: demandToEdit?.current_contract || '',
    depends_on_item: demandToEdit?.depends_on_item || '',
    public_policy: demandToEdit?.public_policy || '',
    is_confidential: demandToEdit?.is_confidential || false,
    confidentiality_basis: demandToEdit?.confidentiality_basis || '',
    // Bloco 4
    budget_source: demandToEdit?.budget_source || '',
    estimated_value: demandToEdit?.estimated_value || '',
    estimated_source: demandToEdit?.estimated_source || '',
    // Bloco 5
    intended_date: demandToEdit?.intended_date || '',
    f1: demandToEdit?.f1 || 1,
    f2: demandToEdit?.f2 || 1,
    f3: demandToEdit?.f3 || 1,
    f4: demandToEdit?.f4 || 1,
    score_justification: demandToEdit?.score_justification || '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});
  const [openBlocks, setOpenBlocks] = useState({ 1: true, 2: true, 3: false, 4: true, 5: true });

  const toggleBlock = (n) => setOpenBlocks(prev => ({ ...prev, [n]: !prev[n] }));

  const validate = () => {
    const errs = {};
    if (!formData.description) errs.description = 'Obrigatório';
    if (!formData.catmat_code) errs.catmat_code = 'Obrigatório';
    if (!formData.estimated_value || Number(formData.estimated_value) <= 0) errs.estimated_value = 'Valor inválido';
    if (!formData.intended_date) errs.intended_date = 'Obrigatório';
    if (!formData.strategic_alignment) errs.strategic_alignment = 'Obrigatório';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) {
      setError('Preencha todos os campos obrigatórios destacados em vermelho.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      if (isEditing) {
        await api.put(`/demands/${demandToEdit.id}/`, formData);
      } else {
        await api.post('/demands/', formData);
      }
      onDemandCreated();
    } catch (err) {
      const apiMsg =
        err.response?.data?.detail ||
        (typeof err.response?.data === 'string' ? err.response?.data : null) ||
        JSON.stringify(err.response?.data) ||
        'Erro ao salvar.';
      setError(`Falha: ${apiMsg}`);
    } finally {
      setLoading(false);
    }
  };

  const inputCls = (field) =>
    `w-full px-3 py-2 bg-slate-900 border ${errors[field] ? 'border-red-500' : 'border-slate-700'} rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500`;

  const BlockHeader = ({ num, icon, title, color }) => (
    <button
      type="button"
      onClick={() => toggleBlock(num)}
      className={`w-full flex items-center justify-between px-4 py-3 rounded-t-lg text-left font-semibold text-sm ${color}`}
    >
      <span>{icon} {title}</span>
      <span className="text-xs opacity-70">{openBlocks[num] ? '▼' : '►'}</span>
    </button>
  );

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-md text-white space-y-4">
      {isEditing && demandToEdit?.rejection_reason && (
        <div className="p-4 bg-red-950/60 border border-red-500/50 rounded-lg text-xs space-y-1">
          <p className="font-bold text-red-400 uppercase tracking-wide">Ajuste Solicitado pelo Diretor:</p>
          <p className="text-red-200 text-sm italic">"{demandToEdit.rejection_reason}"</p>
          <p className="text-slate-400 text-[11px] pt-1">Altere os campos necessários. Ao salvar, a prioridade será recalculada e o item reenviado à Diretoria.</p>
        </div>
      )}

      <div className="flex items-center justify-between pb-4 border-b border-slate-700 mb-2">
        <div>
          <h2 className="text-xl font-bold">Registro de Necessidade — PLAC 2027</h2>
          <p className="text-slate-400 text-xs mt-0.5">Diretriz nº ___/2026, Anexo I — Levantamento de Necessidades</p>
        </div>
        <button type="button" onClick={onCancel} className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1.5 rounded transition">Voltar</button>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/60 rounded-lg text-red-400 text-sm">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* ═══ BLOCO 1 — Identificação ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={1} icon="🏢" title="Bloco 1 — Identificação" color="bg-slate-700/50 text-blue-300" />
          {openBlocks[1] && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Diretoria</label>
                <select value={formData.directorate} onChange={(e) => setFormData({...formData, directorate: e.target.value})} className={inputCls('directorate')}>
                  <option value="">Selecione...</option>
                  <option value="1000 - Presidência">1000 - Presidência</option>
                  <option value="2000 - Diretoria de Negócios">2000 - Diretoria de Negócios</option>
                  <option value="3000 - Diretoria Técnico-Operacional">3000 - Diretoria Técnico-Operacional</option>
                  <option value="4000 - DAFRI">4000 - DAFRI</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Gerência Demandante</label>
                <input type="text" value={formData.management_unit} onChange={(e) => setFormData({...formData, management_unit: e.target.value})} className={inputCls('management_unit')} placeholder="Ex: 3600 - Gerência de Manutenção" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Responsável pelo Registro</label>
                <input type="text" value={formData.responsible_name} onChange={(e) => setFormData({...formData, responsible_name: e.target.value})} className={inputCls('responsible_name')} placeholder="Nome completo" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">E-mail do Responsável</label>
                <input type="email" value={formData.responsible_email} onChange={(e) => setFormData({...formData, responsible_email: e.target.value})} className={inputCls('responsible_email')} placeholder="nome@telebras.com.br" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Natureza *</label>
                <select value={formData.nature_type} onChange={(e) => setFormData({...formData, nature_type: e.target.value})} className={inputCls('nature_type')}>
                  <option value="NOVA">Nova contratação</option>
                  <option value="PRORROGACAO">Prorrogação</option>
                  <option value="ADITIVO">Aditivo</option>
                  <option value="REAJUSTE">Reajuste</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* ═══ BLOCO 2 — Objeto ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={2} icon="📦" title="Bloco 2 — Objeto" color="bg-slate-700/50 text-emerald-300" />
          {openBlocks[2] && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-400 mb-1">Descrição do Objeto *</label>
                <textarea rows="3" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className={inputCls('description')} placeholder="Ex: Manutenção preventiva e corretiva de grupos geradores..." />
                {errors.description && <p className="text-red-400 text-xs mt-1">{errors.description}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Tipo do Objeto *</label>
                <select value={formData.item_type} onChange={(e) => setFormData({...formData, item_type: e.target.value})} className={inputCls('item_type')}>
                  <option value="BEM">Bem</option>
                  <option value="SERVICO">Serviço</option>
                  <option value="TI">Tecnologia da Informação (TI)</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">CATMAT/CATSER *</label>
                <CatmatAutocomplete
                  value={formData.catmat_code}
                  onChange={(val) => setFormData({...formData, catmat_code: val})}
                  error={!!errors.catmat_code}
                  itemType={formData.item_type}
                />
                {errors.catmat_code && <p className="text-red-400 text-xs mt-1">{errors.catmat_code}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Quantidade</label>
                <input type="number" min="1" value={formData.quantity} onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value) || 1})} className={inputCls('quantity')} />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Unidade</label>
                <input type="text" value={formData.unit} onChange={(e) => setFormData({...formData, unit: e.target.value})} className={inputCls('unit')} placeholder="Ex: Serviço anual, Unidade, Lote" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-400 mb-1">Justificativa da Necessidade</label>
                <textarea rows="2" value={formData.justification} onChange={(e) => setFormData({...formData, justification: e.target.value})} className={inputCls('justification')} placeholder="Ex: Contrato vigente encerra em 31/08/2027..." />
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-400 mb-1">Objetivo Estratégico do PEI *</label>
                <input type="text" value={formData.strategic_alignment} onChange={(e) => setFormData({...formData, strategic_alignment: e.target.value})} className={inputCls('strategic_alignment')} placeholder="Ex: 6. Prover soluções robustas e resilientes..." />
                {errors.strategic_alignment && <p className="text-red-400 text-xs mt-1">{errors.strategic_alignment}</p>}
              </div>
            </div>
          )}
        </div>

        {/* ═══ BLOCO 3 — Vinculações ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={3} icon="🔗" title="Bloco 3 — Vinculações (opcional)" color="bg-slate-700/50 text-purple-300" />
          {openBlocks[3] && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Contrato Vigente (nº e processo)</label>
                <input type="text" value={formData.current_contract} onChange={(e) => setFormData({...formData, current_contract: e.target.value})} className={inputCls('current_contract')} placeholder="Ex: Contrato 45/2023 — Processo 0001/2023" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Depende do Item Nº</label>
                <input type="text" value={formData.depends_on_item} onChange={(e) => setFormData({...formData, depends_on_item: e.target.value})} className={inputCls('depends_on_item')} placeholder="Nº do item" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Projeto ou Política Pública</label>
                <input type="text" value={formData.public_policy} onChange={(e) => setFormData({...formData, public_policy: e.target.value})} className={inputCls('public_policy')} placeholder="Ex: Programa de continuidade operacional" />
              </div>
              <div className="flex items-center gap-4 pt-5">
                <label className="flex items-center space-x-2 text-sm text-slate-300 cursor-pointer">
                  <input type="checkbox" checked={formData.is_confidential} onChange={(e) => setFormData({...formData, is_confidential: e.target.checked})} className="rounded bg-slate-900 border-slate-700" />
                  <span>Sujeito a Sigilo</span>
                </label>
              </div>
              {formData.is_confidential && (
                <div className="md:col-span-2">
                  <label className="block text-xs font-medium text-slate-400 mb-1">Fundamento do Sigilo</label>
                  <input type="text" value={formData.confidentiality_basis} onChange={(e) => setFormData({...formData, confidentiality_basis: e.target.value})} className={inputCls('confidentiality_basis')} placeholder="Base legal ou justificativa" />
                </div>
              )}
            </div>
          )}
        </div>

        {/* ═══ BLOCO 4 — Valores ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={4} icon="💰" title="Bloco 4 — Valores" color="bg-slate-700/50 text-amber-300" />
          {openBlocks[4] && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Fonte Orçamentária</label>
                <select value={formData.budget_source} onChange={(e) => setFormData({...formData, budget_source: e.target.value})} className={inputCls('budget_source')}>
                  <option value="">Selecione...</option>
                  <option value="PDG">PDG - Programa de Dispêndios Globais</option>
                  <option value="LOA">LOA - Lei Orçamentária Anual</option>
                  <option value="EMENDA">Emenda Parlamentar</option>
                  <option value="OUTRO">Outro</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Valor Estimado 2027 (R$) *</label>
                <input type="number" step="0.01" value={formData.estimated_value} onChange={(e) => setFormData({...formData, estimated_value: e.target.value})} className={inputCls('estimated_value')} placeholder="0,00" />
                {errors.estimated_value && <p className="text-red-400 text-xs mt-1">{errors.estimated_value}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Fonte da Estimativa</label>
                <input type="text" value={formData.estimated_source} onChange={(e) => setFormData({...formData, estimated_source: e.target.value})} className={inputCls('estimated_source')} placeholder="Ex: Contrato vigente reajustado pelo IPCA" />
              </div>
            </div>
          )}
        </div>

        {/* ═══ BLOCO 5 — Prazos e Priorização ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={5} icon="⚡" title="Bloco 5 — Prazos e Priorização" color="bg-slate-700/50 text-red-300" />
          {openBlocks[5] && (
            <div className="p-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Data Pretendida de Assinatura *</label>
                  <input type="date" value={formData.intended_date} onChange={(e) => setFormData({...formData, intended_date: e.target.value})} className={inputCls('intended_date')} />
                  {errors.intended_date && <p className="text-red-400 text-xs mt-1">{errors.intended_date}</p>}
                </div>
              </div>

              <h4 className="text-sm font-semibold text-blue-400 pt-2">Questionário de Priorização (Notas: 1, 3 ou 5)</h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { id: 'f1', label: 'F1 — Criticidade (Peso 30)', desc: 'Impacto em caso de não contratação' },
                  { id: 'f2', label: 'F2 — Descontinuidade (Peso 30)', desc: 'Risco de interrupção de serviço por vencimento contratual' },
                  { id: 'f3', label: 'F3 — Obrigação Legal (Peso 25)', desc: 'Existência de prazo fatal ou obrigação regulatória' },
                  { id: 'f4', label: 'F4 — Materialidade (Peso 15)', desc: 'Relevância financeira e orçamentária' },
                ].map((f) => (
                  <div key={f.id} className="p-3 bg-slate-900/70 border border-slate-700 rounded-lg">
                    <label className="block text-sm font-medium text-slate-200">{f.label}</label>
                    <p className="text-xs text-slate-400 mb-2">{f.desc}</p>
                    <div className="flex gap-4">
                      {[1, 3, 5].map((val) => (
                        <label key={val} className="flex items-center space-x-1.5 cursor-pointer text-sm">
                          <input type="radio" name={f.id} value={val} checked={formData[f.id] === val} onChange={() => setFormData({ ...formData, [f.id]: val })} className="text-blue-600 focus:ring-blue-500" />
                          <span>Nota {val}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Justificativa das Notas</label>
                <textarea rows="2" value={formData.score_justification} onChange={(e) => setFormData({...formData, score_justification: e.target.value})} className={inputCls('score_justification')} placeholder="Ex: F1: energia de retaguarda das estações. F2: contrato expira sem possibilidade de prorrogação..." />
              </div>
            </div>
          )}
        </div>

        {/* ═══ Botões ═══ */}
        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          <button type="button" onClick={onCancel} className="px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition">Cancelar</button>
          <button type="submit" disabled={loading} className={`px-6 py-2.5 ${isEditing ? 'bg-amber-600 hover:bg-amber-700' : 'bg-blue-600 hover:bg-blue-700'} text-white font-medium rounded-lg text-sm shadow transition`}>
            {loading ? 'Processando Cálculo...' : isEditing ? '✓ Salvar Ajustes e Reenviar à Diretoria' : 'Salvar Necessidade'}
          </button>
        </div>
      </form>
    </div>
  );
}
