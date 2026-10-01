import React, { useState } from 'react';
import api from '../services/api';

export default function TribunalIA({ onApplyToForm }) {
  const [formData, setFormData] = useState({
    objeto: '',
    valor_estimado: '',
    regime_lei: '14.133/2021',
    tipo_objeto: 'SERVICO',
    is_exclusivo: false,
    is_notoria_especializacao: false,
    is_credenciamento: false,
    is_emergencial: false,
    is_continuo: true,
  });

  const [loading, setLoading] = useState(false);
  const [vereditoData, setVereditoData] = useState(null);
  const [error, setError] = useState('');
  const [applied, setApplied] = useState(false);

  // Cenários rápidos de teste para o usuário experimentar
  const quickScenarios = [
    {
      label: 'Oracle Premier Support (Exclusivo)',
      objeto: 'Suporte técnico especializado Premier Support e atualização de licenças de banco de dados Oracle Database Enterprise Edition.',
      valor: 645000,
      lei: '14.133/2021',
      tipo: 'TI',
      exclusivo: true,
      notoria: false,
      credenciamento: false,
      emergencial: false,
      continuo: true
    },
    {
      label: 'Manutenção Nobreaks (Dispensa R$ 48k)',
      objeto: 'Manutenção preventiva e corretiva de nobreaks e grupos geradores da Estação Satelital.',
      valor: 48200,
      lei: '14.133/2021',
      tipo: 'ENGENHARIA',
      exclusivo: false,
      notoria: false,
      credenciamento: false,
      emergencial: false,
      continuo: false
    },
    {
      label: 'Credenciamento Clínicas Médicas (Art. 79)',
      objeto: 'Credenciamento de clínicas médicas e psicológicas para exames periódicos e admissionais de colaboradores.',
      valor: 120000,
      lei: '14.133/2021',
      tipo: 'SERVICO',
      exclusivo: false,
      notoria: false,
      credenciamento: true,
      emergencial: false,
      continuo: true
    },
    {
      label: 'Parecer Notória Especialização (Lei 13.303)',
      objeto: 'Contratação de parecer jurídico especializado e estratégico em regulação de telecomunicações com jurista de notória especialização.',
      valor: 85000,
      lei: '13.303/2016',
      tipo: 'SERVICO',
      exclusivo: false,
      notoria: true,
      credenciamento: false,
      emergencial: false,
      continuo: false
    },
    {
      label: '500 Laptops Corporativos (Pregão)',
      objeto: 'Aquisição de 500 computadores portáteis com processadores de alta performance para renovação do parque corporativo.',
      valor: 2500000,
      lei: '14.133/2021',
      tipo: 'BEM',
      exclusivo: false,
      notoria: false,
      credenciamento: false,
      emergencial: false,
      continuo: false
    }
  ];

  const applyScenario = (sc) => {
    setFormData({
      objeto: sc.objeto,
      valor_estimado: sc.valor,
      regime_lei: sc.lei,
      tipo_objeto: sc.tipo,
      is_exclusivo: sc.exclusivo,
      is_notoria_especializacao: sc.notoria,
      is_credenciamento: sc.credenciamento,
      is_emergencial: sc.emergencial,
      is_continuo: sc.continuo
    });
    setVereditoData(null);
    setApplied(false);
  };

  const handleJulgar = async (e) => {
    e?.preventDefault();
    if (!formData.objeto.trim()) {
      setError('Por favor, informe a descrição ou objeto da contratação pretendida.');
      return;
    }
    setError('');
    setLoading(true);
    setApplied(false);

    try {
      const res = await api.post('/tribunal-ia/inferir/', {
        objeto: formData.objeto,
        valor_estimado: parseFloat(formData.valor_estimado) || 0,
        regime_lei: formData.regime_lei,
        tipo_objeto: formData.tipo_objeto,
        is_exclusivo: formData.is_exclusivo,
        is_notoria_especializacao: formData.is_notoria_especializacao,
        is_credenciamento: formData.is_credenciamento,
        is_emergencial: formData.is_emergencial,
        is_continuo: formData.is_continuo
      });
      setVereditoData(res.data);
    } catch (err) {
      console.error(err);
      setError('Falha ao conectar com o Tribunal da IA.');
    } finally {
      setLoading(false);
    }
  };

  const handleApply = () => {
    if (!vereditoData || !onApplyToForm) return;
    onApplyToForm(vereditoData);
    setApplied(true);
    setTimeout(() => setApplied(false), 3000);
  };

  return (
    <div className="space-y-6">
      {/* Bloco de Entrada do Tribunal */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-slate-700 gap-2">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>⚖️</span> Tribunal da IA — Julgamento de Enquadramento Legal
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Inferência automática de Modalidade, Amparo Legal PNCP, Prazos de Vigência, Justificativa e Matriz de Riscos TCU
            </p>
          </div>
          <span className="text-xs bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-3 py-1 rounded-full font-mono self-start md:self-auto">
            Lei 14.133 / Lei 13.303
          </span>
        </div>

        {/* Botões de Cenários Rápidos */}
        <div className="mt-4 pt-2">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-2">
            💡 Simulação Rápida (Clique para carregar cenários reais da Telebras):
          </label>
          <div className="flex flex-wrap gap-2">
            {quickScenarios.map((sc, i) => (
              <button
                key={i}
                type="button"
                onClick={() => applyScenario(sc)}
                className="text-xs bg-slate-900 hover:bg-blue-900/50 hover:border-blue-500/60 text-slate-300 px-3 py-1.5 rounded-lg border border-slate-700 transition"
              >
                {sc.label}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleJulgar} className="mt-5 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Descrição do Objeto ou Necessidade Pretendida *
              </label>
              <textarea
                rows="3"
                value={formData.objeto}
                onChange={(e) => setFormData({ ...formData, objeto: e.target.value })}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: Aquisição de licenças e suporte técnico especializado da fabricante Oracle com exclusividade..."
              />
            </div>

            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Valor Estimado Total (R$)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={formData.valor_estimado}
                  onChange={(e) => setFormData({ ...formData, valor_estimado: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="0,00"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Regime Jurídico Preferencial
                </label>
                <select
                  value={formData.regime_lei}
                  onChange={(e) => setFormData({ ...formData, regime_lei: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="14.133/2021">Lei nº 14.133/2021 (Nova Lei de Licitações)</option>
                  <option value="13.303/2016">Lei nº 13.303/2016 (Lei das Estatais - Telebras)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">
                Natureza / Tipo do Objeto
              </label>
              <select
                value={formData.tipo_objeto}
                onChange={(e) => setFormData({ ...formData, tipo_objeto: e.target.value })}
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="SERVICO">Serviço em Geral</option>
                <option value="BEM">Aquisição de Bem / Material</option>
                <option value="TI">Tecnologia da Informação (TI)</option>
                <option value="ENGENHARIA">Obras ou Serviços de Engenharia</option>
              </select>
            </div>

            {/* Checkboxes de Parâmetros Críticos de Julgamento */}
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700 space-y-2">
              <label className="text-[11px] font-semibold uppercase text-slate-400 block">
                Características de Mercado / Fornecedor:
              </label>
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_exclusivo}
                    onChange={(e) => setFormData({ ...formData, is_exclusivo: e.target.checked })}
                    className="rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Fornecedor Exclusivo</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_notoria_especializacao}
                    onChange={(e) => setFormData({ ...formData, is_notoria_especializacao: e.target.checked })}
                    className="rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Notória Especialização</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_credenciamento}
                    onChange={(e) => setFormData({ ...formData, is_credenciamento: e.target.checked })}
                    className="rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Rede Credenciada</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.is_emergencial}
                    onChange={(e) => setFormData({ ...formData, is_emergencial: e.target.checked })}
                    className="rounded bg-slate-800 border-slate-600 text-blue-600 focus:ring-blue-500"
                  />
                  <span>Emergência / Urgência</span>
                </label>
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm px-6 py-2.5 rounded-lg shadow-lg flex items-center gap-2 transition"
            >
              {loading ? (
                <>
                  <span className="animate-spin text-base">⚙️</span>
                  <span>O Tribunal da IA está deliberando...</span>
                </>
              ) : (
                <>
                  <span>⚖️</span>
                  <span>Julgar Enquadramento com Tribunal da IA</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Exibição da Sessão de Julgamento / Veredito */}
      {vereditoData && (
        <div className="space-y-5 animate-fade-in">
          {/* Barra de Ação Superior do Veredito */}
          <div className="bg-gradient-to-r from-blue-900/60 to-indigo-900/60 border border-blue-500/40 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center gap-3">
              <span className="text-3xl">👨‍⚖️</span>
              <div>
                <p className="text-xs uppercase font-bold tracking-wider text-blue-300">Veredito Conclusivo do Tribunal da IA</p>
                <h3 className="text-lg font-extrabold text-white">
                  Modalidade Recomendada: {vereditoData.veredito.modalidade_nome}
                </h3>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleApply}
                className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold px-5 py-2.5 rounded-lg shadow-md flex items-center gap-2 transition"
              >
                <span>📥</span>
                <span>{applied ? '✓ Aplicado no Formulário!' : 'Aplicar no Formulário de Compra'}</span>
              </button>
            </div>
          </div>

          {/* Grid dos 3 Corpos Julgadores */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
            {/* 1. Juiz Relator (Mérito & Base Legal) */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow space-y-3">
              <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wide flex items-center gap-1.5">
                  <span>🏛️</span> Voto do Relator (Mérito)
                </span>
                <span className="text-[11px] bg-slate-900 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">
                  ID PNCP: {vereditoData.veredito.modalidade_id}
                </span>
              </div>

              <div>
                <p className="text-xs text-slate-400 font-medium">Fundamentação Legal (Amparo Oficial):</p>
                <p className="text-sm font-bold text-white mt-0.5">
                  {vereditoData.veredito.amparo_legal_nome}
                </p>
              </div>

              <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-700 text-xs space-y-1">
                <p className="text-slate-400">Texto Oficial do Amparo:</p>
                <p className="text-slate-200 italic font-serif">
                  "{vereditoData.veredito.amparo_legal_texto}"
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-400 font-medium">Tese Jurídica Sustentada:</p>
                <p className="text-xs text-slate-300 mt-1 leading-relaxed bg-slate-900/50 p-2.5 rounded border border-slate-700">
                  {vereditoData.veredito.tese_juridica}
                </p>
              </div>
            </div>

            {/* 2. Auditor de Riscos TCU */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow space-y-3">
              <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                <span className="text-xs font-bold text-amber-400 uppercase tracking-wide flex items-center gap-1.5">
                  <span>🛡️</span> Parecer de Riscos TCU
                </span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                    vereditoData.auditoria_riscos_tcu.nivel_risco === 'ALTO'
                      ? 'bg-red-900/60 text-red-300 border border-red-700'
                      : vereditoData.auditoria_riscos_tcu.nivel_risco === 'MEDIO'
                      ? 'bg-yellow-900/60 text-yellow-300 border border-yellow-700'
                      : 'bg-emerald-900/60 text-emerald-300 border border-emerald-700'
                  }`}
                >
                  Risco: {vereditoData.auditoria_riscos_tcu.nivel_risco}
                </span>
              </div>

              <div className="space-y-2">
                <p className="text-xs text-slate-400 font-medium">Alertas de Auditoria e Jurisprudência:</p>
                {vereditoData.auditoria_riscos_tcu.alertas.map((alerta, idx) => (
                  <div key={idx} className="p-2.5 bg-slate-900/80 rounded border border-amber-500/20 text-xs text-amber-200 leading-snug">
                    {alerta}
                  </div>
                ))}
              </div>

              <div>
                <p className="text-xs text-slate-400 font-medium mb-1">Checklist Obrigatório de Instrução:</p>
                <ul className="text-xs text-slate-300 space-y-1 list-disc list-inside bg-slate-900/50 p-2.5 rounded border border-slate-700">
                  {vereditoData.auditoria_riscos_tcu.checklist_obrigatorio.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* 3. Assessor Técnico (Instrução Processual e Campos) */}
            <div className="bg-slate-800 border border-slate-700 rounded-xl p-5 shadow space-y-3">
              <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                <span className="text-xs font-bold text-purple-400 uppercase tracking-wide flex items-center gap-1.5">
                  <span>📋</span> Minuta Pronta para PNCP
                </span>
                <span className="text-[11px] bg-slate-900 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">
                  Vigência: 12 meses
                </span>
              </div>

              <div>
                <p className="text-xs text-slate-400 font-medium">Objeto Lapidado:</p>
                <p className="text-xs text-slate-200 bg-slate-900 p-2 rounded border border-slate-700 font-sans mt-0.5">
                  {vereditoData.dados_formulario_compra.objeto}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-900 p-2 rounded border border-slate-700">
                  <p className="text-slate-400 text-[10px]">Data Início Estimada:</p>
                  <p className="font-bold text-white">{vereditoData.dados_formulario_compra.data_inicio}</p>
                </div>
                <div className="bg-slate-900 p-2 rounded border border-slate-700">
                  <p className="text-slate-400 text-[10px]">Data Fim Estimada:</p>
                  <p className="font-bold text-white">{vereditoData.dados_formulario_compra.data_fim}</p>
                </div>
              </div>

              <div>
                <p className="text-xs text-slate-400 font-medium">Justificativa Inferida:</p>
                <p className="text-xs text-slate-300 bg-slate-900/60 p-2 rounded border border-slate-700 line-clamp-3">
                  {vereditoData.dados_formulario_compra.justificativa}
                </p>
              </div>

              <div>
                <p className="text-xs text-slate-400 font-medium">Estrutura de Itens Sugeridos:</p>
                <div className="text-xs text-slate-300 bg-slate-900 p-2 rounded border border-slate-700 flex justify-between items-center">
                  <span>
                    Item 1 • {vereditoData.dados_formulario_compra.itens[0]?.quantidade}x (
                    {vereditoData.dados_formulario_compra.itens[0]?.unidadeMedida})
                  </span>
                  <span className="font-bold text-emerald-400">
                    R$ {Number(vereditoData.dados_formulario_compra.itens[0]?.valorTotal || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
