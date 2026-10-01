import React, { useState } from 'react';
import api from '../services/api';
import CatmatAutocomplete from '../components/CatmatAutocomplete';

// 10 Modalidades Oficiais e Responsáveis extraídos diretamente de 'FLUXOS DE COMPRAS COM RESPONSÁVEIS GCC.xlsx'
const MODALIDADES_OFICIAIS_GCC = [
  { id: 'PREGAO', nome: 'Pregão Eletrônico (Licitação Ampla)', grupo: 'Licitação Geral (Lei 13.303/2016)', responsavel: 'Marcus / Layllah', dias_real: 31, dias_planilha: 144 },
  { id: 'DISPENSA_TRADICIONAL', nome: 'Dispensa Tradicional Geral (Art. 29 c/c 73)', grupo: 'Dispensas de Licitação', responsavel: 'Marcus / Layllah', dias_real: 15, dias_planilha: 59 },
  { id: 'DISPENSA_BAIXO_VALOR', nome: 'Dispensa Tradicional Baixo Valor (Inc. I e II)', grupo: 'Dispensas de Licitação', responsavel: 'Marcus / Layllah', dias_real: 11, dias_planilha: 60 },
  { id: 'DISPENSA_ELETRONICA', nome: 'Dispensa Eletrônica Comprasnet (IN 67/2021)', grupo: 'Dispensas de Licitação', responsavel: 'Franciele / Roberta', dias_real: 15, dias_planilha: 82 },
  { id: 'DISPENSA_LOCACAO', nome: 'Dispensa para Locação de Imóveis/PoPs (Parecer Padrão)', grupo: 'Dispensas de Licitação', responsavel: 'Vanessa / Thorgarma', dias_real: 20, dias_planilha: 52 },
  { id: 'DISPENSA_ENERGIA', nome: 'Dispensa para Energia Elétrica (Parecer Padrão)', grupo: 'Dispensas de Licitação', responsavel: 'Vanessa / Thorgarma', dias_real: 17, dias_planilha: 48 },
  { id: 'INEXIGIBILIDADE_GERAL', nome: 'Inexigibilidade Geral / Fornecedor Exclusivo (Art. 30)', grupo: 'Inexigibilidades', responsavel: 'Marcus / Layllah', dias_real: 25, dias_planilha: 89 },
  { id: 'INEXIGIBILIDADE_CURSOS', nome: 'Inexigibilidade Capacitação e Cursos (Parecer Padrão)', grupo: 'Inexigibilidades', responsavel: 'Franciele / Roberta', dias_real: 9, dias_planilha: 22 },
  { id: 'INEXIGIBILIDADE_COMPARTILHAMENTO', nome: 'Inexigibilidade Compartilhamento de Infraestrutura', grupo: 'Inexigibilidades', responsavel: 'Vanessa / Thorgarma', dias_real: 28, dias_planilha: 72 },
  { id: 'AFASTAMENTO', nome: 'Contratação Direta por Afastamento de Licitação (Prática nº 88)', grupo: 'Oportunidade Comercial', responsavel: 'Rosilda / Pedro', dias_real: 26, dias_planilha: 90 },
];

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
    procurement_type: demandToEdit?.procurement_type || 'PREGAO',
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

  const modalidadeSelecionada = MODALIDADES_OFICIAIS_GCC.find(m => m.id === formData.procurement_type) || MODALIDADES_OFICIAIS_GCC[0];

  const toggleBlock = (n) => setOpenBlocks(prev => ({ ...prev, [n]: !prev[n] }));

  const validate = () => {
    const errs = {};
    if (!formData.description) errs.description = 'Obrigatório';
    if (!formData.catmat_code) errs.catmat_code = 'Obrigatório';
    if (!formData.estimated_value || Number(formData.estimated_value) <= 0) errs.estimated_value = 'Valor inválido';
    if (!formData.intended_date) errs.intended_date = 'Obrigatório';
    if (!formData.strategic_alignment) errs.strategic_alignment = 'Obrigatório';
    if (!formData.procurement_type) errs.procurement_type = 'Obrigatório';
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
          <h2 className="text-xl font-bold">Fase 1: Registro de Necessidades — PLAC 2027</h2>
          <p className="text-slate-400 text-xs mt-0.5">Levantamento de Necessidades alinhado às 10 esteiras da GCC</p>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={onCancel} className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1.5 rounded transition">
            Voltar
          </button>
        </div>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/60 rounded-lg text-red-400 text-sm">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* ═══ BLOCO 1 — Identificação ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={1} icon="🏢" title="Bloco 1 — Identificação da Área Requisitante" color="bg-slate-700/50 text-blue-300" />
          {openBlocks[1] && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Diretoria *</label>
                <select value={formData.directorate} onChange={(e) => setFormData({...formData, directorate: e.target.value})} className={inputCls('directorate')}>
                  <option value="">Selecione...</option>
                  <option value="1000 - Presidência">1000 - Presidência</option>
                  <option value="2000 - Diretoria de Negócios">2000 - Diretoria de Negócios</option>
                  <option value="3000 - Diretoria Técnico-Operacional">3000 - Diretoria Técnico-Operacional</option>
                  <option value="4000 - DAFRI">4000 - DAFRI</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Gerência Demandante *</label>
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
                  <option value="NOVA">Nova Contratação</option>
                  <option value="RENOVACAO">Renovação Contratual</option>
                  <option value="EXPANSAO">Expansão de Capacidade</option>
                </select>
              </div>
            </div>
          )}
        </div>

        {/* ═══ BLOCO 2 — Objeto ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={2} icon="📦" title="Bloco 2 — Objeto e Especificação Técnica" color="bg-slate-700/50 text-emerald-300" />
          {openBlocks[2] && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-400 mb-1">Descrição Clara do Objeto *</label>
                <textarea rows="3" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className={inputCls('description')} placeholder="Descreva sucintamente o bem ou serviço demandado..." />
                {errors.description && <p className="text-red-400 text-xs mt-1">{errors.description}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Tipo de Objeto</label>
                <select value={formData.item_type} onChange={(e) => setFormData({...formData, item_type: e.target.value})} className={inputCls('item_type')}>
                  <option value="BEM">Bem / Material</option>
                  <option value="SERVICO">Serviço</option>
                  <option value="OBRA">Obra / Engenharia</option>
                  <option value="LOCACAO">Locação</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Código do Catálogo (CATMAT/CATSER) *</label>
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
                <label className="block text-xs font-medium text-slate-400 mb-1">Unidade de Medida</label>
                <input type="text" value={formData.unit} onChange={(e) => setFormData({...formData, unit: e.target.value})} className={inputCls('unit')} placeholder="Ex: Mês, Serviço anual, Unidade" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-xs font-medium text-slate-400 mb-1">Justificativa da Necessidade</label>
                <textarea rows="2" value={formData.justification} onChange={(e) => setFormData({...formData, justification: e.target.value})} className={inputCls('justification')} placeholder="Justifique a necessidade operacional e de negócio..." />
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
            </div>
          )}
        </div>

        {/* ═══ BLOCO 4 — Valores e Orçamento ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={4} icon="💰" title="Bloco 4 — Estimativa Orçamentária" color="bg-slate-700/50 text-amber-300" />
          {openBlocks[4] && (
            <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Fonte Orçamentária</label>
                <select value={formData.budget_source} onChange={(e) => setFormData({...formData, budget_source: e.target.value})} className={inputCls('budget_source')}>
                  <option value="">Selecione...</option>
                  <option value="PDG">PDG - Programa de Dispêndios Globais</option>
                  <option value="LOA">LOA - Lei Orçamentária Anual</option>
                  <option value="OUTRO">Outro</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Valor Estimado (R$) *</label>
                <input type="number" step="0.01" value={formData.estimated_value} onChange={(e) => setFormData({...formData, estimated_value: e.target.value})} className={inputCls('estimated_value')} placeholder="0,00" />
                {errors.estimated_value && <p className="text-red-400 text-xs mt-1">{errors.estimated_value}</p>}
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Fonte da Estimativa</label>
                <input type="text" value={formData.estimated_source} onChange={(e) => setFormData({...formData, estimated_source: e.target.value})} className={inputCls('estimated_source')} placeholder="Ex: Painel de Preços, Contrato vigente" />
              </div>
            </div>
          )}
        </div>

        {/* ═══ BLOCO 5 — Modalidade Oficial da GCC e Prazos ═══ */}
        <div className="border border-slate-700 rounded-lg">
          <BlockHeader num={5} icon="⚡" title="Bloco 5 — Modalidade Oficial da GCC e Prazos Regimentais" color="bg-slate-700/50 text-red-300" />
          {openBlocks[5] && (
            <div className="p-4 space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Seletor Oficial de Modalidade */}
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Modalidade / Esteira Oficial da GCC (Planilha de Referência) *
                  </label>
                  <select
                    value={formData.procurement_type}
                    onChange={(e) => setFormData({...formData, procurement_type: e.target.value})}
                    className={inputCls('procurement_type')}
                  >
                    {MODALIDADES_OFICIAIS_GCC.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.nome} — [Equipe: {m.responsavel}]
                      </option>
                    ))}
                  </select>
                </div>

                {/* Data Pretendida de Assinatura */}
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Data Pretendida de Assinatura / Homologação *
                  </label>
                  <input
                    type="date"
                    value={formData.intended_date}
                    onChange={(e) => setFormData({...formData, intended_date: e.target.value})}
                    className={inputCls('intended_date')}
                  />
                  {errors.intended_date && <p className="text-red-400 text-xs mt-1">{errors.intended_date}</p>}
                </div>
              </div>

              {/* Card de Previsão de Entrega no Setor com os Responsáveis da GCC */}
              {modalidadeSelecionada && (
                <div className="bg-slate-900 border border-indigo-500/40 rounded-xl p-4 space-y-2.5 shadow-inner">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-sm">🏢</span>
                      <span className="text-xs font-bold text-white">
                        {modalidadeSelecionada.nome}
                      </span>
                    </div>
                    <span className="text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2.5 py-0.5 rounded-full">
                      👤 Equipe GCC: {modalidadeSelecionada.responsavel}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1 text-xs">
                    <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-mono block">Duração GCC (IC 99%)</span>
                      <span className="text-sm font-bold text-blue-400 font-mono mt-0.5 block">
                        ~{modalidadeSelecionada.dias_real} dias úteis
                      </span>
                      <span className="text-[9px] text-slate-500">Planilha antiga: {modalidadeSelecionada.dias_planilha} d.u.</span>
                    </div>

                    <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-mono block">Lead Time Total</span>
                      <span className="text-sm font-bold text-emerald-400 font-mono mt-0.5 block">
                        ~{modalidadeSelecionada.dias_real + 25} dias úteis
                      </span>
                      <span className="text-[9px] text-slate-500">ETP/TR (15d) + GCC + Entrega (10d)</span>
                    </div>

                    <div className="bg-slate-950 p-2.5 rounded-lg border border-slate-800">
                      <span className="text-[10px] text-slate-400 uppercase font-mono block">Economia de Folga</span>
                      <span className="text-sm font-bold text-amber-400 font-mono mt-0.5 block">
                        -{modalidadeSelecionada.dias_planilha - modalidadeSelecionada.dias_real} dias
                      </span>
                      <span className="text-[9px] text-slate-500">Previsão estatística auditada</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Questionário de Priorização da Minuta (Anexo II) */}
              <div className="flex items-center justify-between pt-2">
                <h4 className="text-sm font-semibold text-blue-400">
                  Critérios Regimentais de Priorização (Anexo II - Notas: 1, 3 ou 5)
                </h4>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono font-bold text-slate-300">
                    Pontuação: <strong className="text-blue-400 font-mono text-sm">{(formData.f1 * 30) + (formData.f2 * 30) + (formData.f3 * 25) + (formData.f4 * 15)} / 500</strong>
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-black font-mono ${
                    (formData.f2 === 5 || formData.f3 === 5 || ((formData.f1 * 30) + (formData.f2 * 30) + (formData.f3 * 25) + (formData.f4 * 15)) >= 380)
                      ? 'bg-rose-500/20 text-rose-300 border border-rose-500/40'
                      : ((formData.f1 * 30) + (formData.f2 * 30) + (formData.f3 * 25) + (formData.f4 * 15)) >= 240
                      ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                      : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  }`}>
                    {formData.f2 === 5 || formData.f3 === 5 || ((formData.f1 * 30) + (formData.f2 * 30) + (formData.f3 * 25) + (formData.f4 * 15)) >= 380
                      ? 'ALTO (1º Quadrimestre)'
                      : ((formData.f1 * 30) + (formData.f2 * 30) + (formData.f3 * 25) + (formData.f4 * 15)) >= 240
                      ? 'MÉDIO (2º Quadrimestre)'
                      : 'BAIXO (3º Quadrimestre)'}
                  </span>
                </div>
              </div>

              {/* Alerta de Enquadramento Obrigatório ou Vedação */}
              {(formData.f2 === 5 || formData.f3 === 5) && (
                <div className="p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs text-rose-300 flex items-center gap-2">
                  <span>⚡</span>
                  <span>
                    <strong>Enquadramento Obrigatório como ALTO (Item 6 do Anexo II):</strong>{' '}
                    {formData.f2 === 5 ? 'Contrato expira no exercício sem prorrogação (Item 6.b).' : 'Obrigação legal com prazo fatal no exercício (Item 6.a).'}
                    {' '}Envio obrigatório no <strong>1º Quadrimestre (até Abril)</strong>.
                  </span>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {[
                  { id: 'f1', label: 'F1 — Criticidade para Atividade-Fim (Peso 30%)', desc: 'Nota 5: Indispensável à rede / Nota 3: Apoio relevante / Nota 1: Administrativo' },
                  { id: 'f2', label: 'F2 — Risco de Descontinuidade (Peso 30%)', desc: 'Nota 5: Contrato expira sem prorrogação / Nota 3: Prorrogável / Nota 1: Nova' },
                  { id: 'f3', label: 'F3 — Obrigação Legal / Controle (Peso 25%)', desc: 'Nota 5: Prazo fatal de TCU/Anatel no ano / Nota 3: Sem prazo fatal / Nota 1: Discricionária' },
                  { id: 'f4', label: 'F4 — Materialidade Financeira (Peso 15%)', desc: 'Nota 5: 10% maiores valores / Nota 3: 40% seguintes / Nota 1: 50% menores' },
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
                <label className="block text-xs font-medium text-slate-400 mb-1">Justificativa das Notas de Priorização</label>
                <textarea rows="2" value={formData.score_justification} onChange={(e) => setFormData({...formData, score_justification: e.target.value})} className={inputCls('score_justification')} placeholder="Ex: F1: serviço essencial. F2: vencimento iminente sem prorrogação..." />
              </div>
            </div>
          )}
        </div>

        {/* ═══ Botões de Ação ═══ */}
        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          <button type="button" onClick={onCancel} className="px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition">
            Cancelar
          </button>
          <button type="submit" disabled={loading} className={`px-6 py-2.5 ${isEditing ? 'bg-amber-600 hover:bg-amber-700' : 'bg-blue-600 hover:bg-blue-700'} text-white font-medium rounded-lg text-sm shadow transition`}>
            {loading ? 'Processando Cálculo...' : isEditing ? '✓ Salvar Ajustes e Reenviar à Diretoria' : '✓ Salvar Necessidade e Gerar Certidão PLAC'}
          </button>
        </div>
      </form>
    </div>
  );
}
