import React, { useState } from 'react';
import api from '../services/api';

export default function NewDemand({ onDemandCreated, onCancel }) {
  const [formData, setFormData] = useState({
    description: '',
    item_type: 'BEM',
    catmat_code: '',
    estimated_value: '',
    intended_date: '',
    strategic_alignment: '',
    f1: 1,
    f2: 1,
    f3: 1,
    f4: 1,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errors, setErrors] = useState({});

  const validate = () => {
    const errs = {};
    if (!formData.description) errs.description = 'Descrição do objeto é obrigatória';
    if (!formData.catmat_code) errs.catmat_code = 'Classificação CATMAT/CATSER é obrigatória';
    if (!formData.estimated_value || Number(formData.estimated_value) <= 0) {
      errs.estimated_value = 'Informe uma estimativa de valor válida';
    }
    if (!formData.intended_date) errs.intended_date = 'Data pretendida é obrigatória';
    if (!formData.strategic_alignment) errs.strategic_alignment = 'Vinculação estratégica é obrigatória';
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) {
      setError('Por favor, preencha todos os campos obrigatórios destacados em vermelho.');
      return;
    }
    setError('');
    setLoading(true);

    try {
      await api.post('/demands/', formData);
      onDemandCreated();
    } catch (err) {
      const apiMsg =
        err.response?.data?.detail ||
        (typeof err.response?.data === 'string' ? err.response?.data : null) ||
        JSON.stringify(err.response?.data) ||
        'Erro ao registrar necessidade de contratação.';
      setError(`Falha ao salvar: ${apiMsg}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-md text-white">
      <div className="flex items-center justify-between pb-4 border-b border-slate-700 mb-6">
        <div>
          <h2 className="text-xl font-bold">Novo Registro de Necessidade (UC01)</h2>
          <p className="text-slate-400 text-xs mt-0.5">Cadastre o objeto e responda ao questionário de priorização</p>
        </div>
        <button
          type="button"
          onClick={onCancel}
          className="text-xs bg-slate-700 hover:bg-slate-600 text-slate-300 px-3 py-1.5 rounded transition"
        >
          Voltar
        </button>
      </div>

      {error && (
        <div className="mb-6 p-3 bg-red-500/10 border border-red-500/60 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Bloco 1: Dados do Objeto */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Descrição do Objeto *
            </label>
            <textarea
              rows="3"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className={`w-full px-4 py-2 bg-slate-900 border ${
                errors.description ? 'border-red-500' : 'border-slate-700'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
              placeholder="Ex: Aquisição de licenças de software para gestão..."
            />
            {errors.description && <p className="text-red-400 text-xs mt-1">{errors.description}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Tipo de Contratação *</label>
            <select
              value={formData.item_type}
              onChange={(e) => setFormData({ ...formData, item_type: e.target.value })}
              className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="BEM">Bem</option>
              <option value="SERVICO">Serviço</option>
              <option value="TI">Tecnologia da Informação (TI)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Catálogo CATMAT/CATSER *</label>
            <input
              type="text"
              value={formData.catmat_code}
              onChange={(e) => setFormData({ ...formData, catmat_code: e.target.value })}
              className={`w-full px-4 py-2 bg-slate-900 border ${
                errors.catmat_code ? 'border-red-500' : 'border-slate-700'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
              placeholder="Ex: Código ou Item do Catálogo"
            />
            {errors.catmat_code && <p className="text-red-400 text-xs mt-1">{errors.catmat_code}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Estimativa de Valor (R$) *</label>
            <input
              type="number"
              step="0.01"
              value={formData.estimated_value}
              onChange={(e) => setFormData({ ...formData, estimated_value: e.target.value })}
              className={`w-full px-4 py-2 bg-slate-900 border ${
                errors.estimated_value ? 'border-red-500' : 'border-slate-700'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
              placeholder="0,00"
            />
            {errors.estimated_value && <p className="text-red-400 text-xs mt-1">{errors.estimated_value}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Data Pretendida de Assinatura *</label>
            <input
              type="date"
              value={formData.intended_date}
              onChange={(e) => setFormData({ ...formData, intended_date: e.target.value })}
              className={`w-full px-4 py-2 bg-slate-900 border ${
                errors.intended_date ? 'border-red-500' : 'border-slate-700'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
            />
            {errors.intended_date && <p className="text-red-400 text-xs mt-1">{errors.intended_date}</p>}
          </div>

          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-slate-300 mb-1">Vinculação ao Planejamento Estratégico *</label>
            <input
              type="text"
              value={formData.strategic_alignment}
              onChange={(e) => setFormData({ ...formData, strategic_alignment: e.target.value })}
              className={`w-full px-4 py-2 bg-slate-900 border ${
                errors.strategic_alignment ? 'border-red-500' : 'border-slate-700'
              } rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500`}
              placeholder="Ex: Meta 3 - Eficiência Operacional e Transformação Digital"
            />
            {errors.strategic_alignment && (
              <p className="text-red-400 text-xs mt-1">{errors.strategic_alignment}</p>
            )}
          </div>
        </div>

        {/* Bloco 2: Questionário de Priorização F1 a F4 */}
        <div className="pt-4 border-t border-slate-700">
          <h3 className="text-md font-semibold text-blue-400 mb-3">
            Questionário de Priorização (Notas permitidas: 1, 3 ou 5)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { id: 'f1', label: 'F1 - Criticidade (Peso 30)', desc: 'Impacto em caso de não contratação' },
              { id: 'f2', label: 'F2 - Urgência (Peso 30)', desc: 'Sensibilidade de tempo e prazos legais' },
              { id: 'f3', label: 'F3 - Impacto (Peso 25)', desc: 'Abrangência de setores e usuários atendidos' },
              { id: 'f4', label: 'F4 - Materialidade (Peso 15)', desc: 'Relevância financeira e orçamentária' },
            ].map((f) => (
              <div key={f.id} className="p-3 bg-slate-900/70 border border-slate-700 rounded-lg">
                <label className="block text-sm font-medium text-slate-200">{f.label}</label>
                <p className="text-xs text-slate-400 mb-2">{f.desc}</p>
                <div className="flex gap-4">
                  {[1, 3, 5].map((val) => (
                    <label key={val} className="flex items-center space-x-1.5 cursor-pointer text-sm">
                      <input
                        type="radio"
                        name={f.id}
                        value={val}
                        checked={formData[f.id] === val}
                        onChange={() => setFormData({ ...formData, [f.id]: val })}
                        className="text-blue-600 focus:ring-blue-500"
                      />
                      <span>Nota {val}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-slate-700">
          <button
            type="button"
            onClick={onCancel}
            className="px-5 py-2.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-sm transition"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-sm shadow transition"
          >
            {loading ? 'Processando Cálculo...' : 'Salvar Necessidade'}
          </button>
        </div>
      </form>
    </div>
  );
}
