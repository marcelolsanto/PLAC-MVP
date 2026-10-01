import React, { useState, useEffect } from 'react';
import api from '../services/api';
import TribunalIA from './TribunalIA';
import GuiaTribunalIA from './GuiaTribunalIA';
import CatmatAutocomplete from './CatmatAutocomplete';

export default function ComprasModule() {
  const [activeSubTab, setActiveSubTab] = useState('tribunal'); // 'tribunal', 'planilha', 'formulario', 'guia'
  
  // Memória do Formulário Oficial da Compra (API_LINK)
  const [formData, setFormData] = useState({
    orgao_responsavel: '00336701000104 - TELEBRAS Sede Brasília/DF',
    titulo: '',
    numero_processo: '',
    justificativa_nao_planejada: '',
    modo_disputa: 'Não se aplica',
    modalidade_id: 8,
    modalidade_nome: 'Dispensa de Licitação',
    amparo_legal_id: 62,
    tipo_documento_id: 1,
    proc_eletronico: 'Sim',
    link_processo_eletronico: '925150 - Processo Digital',
    categoria: 'Serviços',
    data_inicio: new Date().toISOString().split('T')[0],
    data_fim: new Date(Date.now() + 365 * 86400000).toISOString().split('T')[0],
    objeto: '',
    informacoes_complementares: '',
    fornecedor_nome: '',
    fornecedor_cnpj: '',
  });

  const [itensLista, setItensLista] = useState([]);
  const [amparosDisponiveis, setAmparosDisponiveis] = useState([]);
  const [amparoSelecionadoDetalhe, setAmparoSelecionadoDetalhe] = useState(null);

  // Memória de Planilha em Lote
  const [comprasLote, setComprasLote] = useState([]);
  const [buscaPlanilha, setBuscaPlanilha] = useState('');
  const [loadingPlanilha, setLoadingPlanilha] = useState(false);

  // Novo Item Rápido
  const [novoItem, setNovoItem] = useState({
    tipo: 'S',
    codigo: '',
    descricao: '',
    quantidade: 12,
    valor_unitario: 0,
    unidade: 'MÊS'
  });

  // Mensagens e Notificações
  const [statusMsg, setStatusMsg] = useState({ tipo: '', texto: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Carregar catálogo de Amparos Oficiais do Backend
  const carregarAmparos = async (modId) => {
    try {
      const res = await api.get(`/amparos-legais/?modalidade_id=${modId}`);
      const lista = res.data?.resultado || [];
      setAmparosDisponiveis(lista);
      if (lista.length > 0) {
        setFormData(prev => ({ ...prev, amparo_legal_id: lista[0].id }));
        setAmparoSelecionadoDetalhe(lista[0]);
      }
    } catch (e) {
      console.error("Erro ao carregar amparos", e);
    }
  };

  useEffect(() => {
    carregarAmparos(formData.modalidade_id);
  }, [formData.modalidade_id]);

  // Handler para quando o Tribunal da IA emite o veredito e o usuário clica em "Aplicar no Formulário"
  const handleApplyTribunal = (tribunalResult) => {
    const dadosForm = tribunalResult.dados_formulario_compra;
    const veredito = tribunalResult.veredito;

    setFormData(prev => ({
      ...prev,
      titulo: dadosForm.titulo,
      numero_processo: dadosForm.numero_processo,
      objeto: dadosForm.objeto,
      justificativa_nao_planejada: dadosForm.justificativa_nao_planejada,
      informacoes_complementares: dadosForm.informacoes_complementares,
      modalidade_id: veredito.modalidade_id,
      modalidade_nome: veredito.modalidade_nome,
      amparo_legal_id: veredito.amparo_legal_id,
      data_inicio: dadosForm.data_inicio,
      data_fim: dadosForm.data_fim,
      modo_disputa: dadosForm.modo_disputa
    }));

    if (dadosForm.itens && dadosForm.itens.length > 0) {
      setItensLista(dadosForm.itens);
    }

    setAmparoSelecionadoDetalhe({
      id: veredito.amparo_legal_id,
      nome: veredito.amparo_legal_nome,
      descricao: veredito.amparo_legal_texto
    });

    setStatusMsg({
      tipo: 'sucesso',
      texto: `✅ Veredito do Tribunal da IA aplicado com sucesso no formulário de compra!`
    });

    setActiveSubTab('formulario');
  };

  // Handler para processar planilha de contratos em lote
  const handleProcessarPlanilha = async (e) => {
    e?.preventDefault();
    setLoadingPlanilha(true);
    setStatusMsg({ tipo: '', texto: '' });
    try {
      const res = await api.post('/compras/extrair-planilha/');
      setComprasLote(res.data || []);
      setStatusMsg({
        tipo: 'sucesso',
        texto: `✅ ${res.data?.length || 0} processos de contratos e ARPs extraídos com sucesso da planilha!`
      });
    } catch (err) {
      console.error(err);
      setStatusMsg({ tipo: 'erro', texto: 'Falha ao processar planilha.' });
    } finally {
      setLoadingPlanilha(false);
    }
  };

  // Preencher formulário a partir de um contrato da planilha
  const handlePreencherDaPlanilha = (itemLote) => {
    const modRaw = String(itemLote.modalidade_raw || '').toUpperCase();
    let modId = 8;
    let modNome = 'Dispensa de Licitação';
    if (modRaw.includes('INEXIG')) {
      modId = 9;
      modNome = 'Inexigibilidade de Licitação';
    } else if (modRaw.includes('CREDEN')) {
      modId = 10;
      modNome = 'Credenciamento';
    } else if (modRaw.includes('PREG')) {
      modId = 6;
      modNome = 'Pregão Eletrônico';
    }

    setFormData(prev => ({
      ...prev,
      titulo: itemLote.numero_contrato || `Contrato ${itemLote.numero_processo}`,
      numero_processo: itemLote.numero_processo || '',
      objeto: itemLote.objeto || '',
      justificativa_nao_planejada: itemLote.justificativa || '',
      informacoes_complementares: itemLote.informacoes_complementares || '',
      fornecedor_nome: itemLote.fornecedor || '',
      fornecedor_cnpj: itemLote.cnpj_cpf || '',
      modalidade_id: modId,
      modalidade_nome: modNome,
      data_inicio: itemLote.data_inicio_estimada || prev.data_inicio,
      data_fim: itemLote.data_fim_estimada || prev.data_fim
    }));

    if (itemLote.itens) {
      setItensLista(itemLote.itens);
    } else {
      setItensLista([{
        numeroItem: 1,
        descricao: itemLote.objeto || 'Serviço Contratado',
        quantidade: itemLote.num_parcelas || 12,
        valorUnitarioEstimado: itemLote.valor_parcela || 0,
        valorTotal: itemLote.valor_contrato || 0,
        unidadeMedida: 'MÊS',
        tipo: 'S'
      }]);
    }

    setStatusMsg({
      tipo: 'sucesso',
      texto: `✅ Contrato ${itemLote.numero_contrato || itemLote.numero_processo} carregado no formulário!`
    });
    setActiveSubTab('formulario');
  };

  // Adicionar item manualmente à lista
  const handleAddItem = () => {
    if (!novoItem.descricao.trim()) return;
    const total = (parseFloat(novoItem.quantidade) || 1) * (parseFloat(novoItem.valor_unitario) || 0);
    const itemToAdd = {
      numeroItem: itensLista.length + 1,
      descricao: novoItem.descricao,
      tipo: novoItem.tipo,
      codigo: novoItem.codigo || '0000',
      quantidade: parseFloat(novoItem.quantidade) || 1,
      unidadeMedida: novoItem.unidade,
      valorUnitarioEstimado: parseFloat(novoItem.valor_unitario) || 0,
      valorTotal: total
    };
    setItensLista([...itensLista, itemToAdd]);
    setNovoItem({ tipo: 'S', codigo: '', descricao: '', quantidade: 12, valor_unitario: 0, unidade: 'MÊS' });
  };

  const handleRemoveItem = (index) => {
    setItensLista(itensLista.filter((_, i) => i !== index));
  };

  // Valor total acumulado da contratação
  const valorTotalGeral = itensLista.reduce((acc, curr) => acc + (parseFloat(curr.valorTotal || curr.valor_total) || 0), 0);

  // Submissão Final do Cadastro
  const handleSalvarCompra = async () => {
    if (!formData.objeto.trim()) {
      setStatusMsg({ tipo: 'erro', texto: 'Por favor, informe a descrição do objeto.' });
      return;
    }
    if (itensLista.length === 0) {
      setStatusMsg({ tipo: 'erro', texto: 'Adicione pelo menos um item à lista de compras.' });
      return;
    }

    setIsSubmitting(true);
    setStatusMsg({ tipo: '', texto: '' });

    try {
      const payload = {
        ...formData,
        valor_total_estimado: valorTotalGeral,
        itens: itensLista
      };
      const res = await api.post('/compras/cadastrar/', payload);
      setStatusMsg({
        tipo: 'sucesso',
        texto: `🎉 ${res.data?.mensagem || 'Contratação cadastrada com sucesso!'}`
      });
    } catch (err) {
      console.error(err);
      setStatusMsg({ tipo: 'erro', texto: 'Falha ao salvar a compra no servidor.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Barra de Navegação Interna do Módulo de Compras */}
      <div className="bg-slate-800 border border-slate-700 rounded-xl p-2 flex flex-wrap gap-2 shadow-md">
        <button
          type="button"
          onClick={() => setActiveSubTab('tribunal')}
          className={`flex items-center gap-2 text-xs font-semibold px-4 py-2.5 rounded-lg transition ${
            activeSubTab === 'tribunal'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-300 hover:bg-slate-700/60'
          }`}
        >
          <span>⚖️</span>
          <span>Tribunal da IA (Julgamento)</span>
        </button>

        <button
          type="button"
          onClick={() => setActiveSubTab('formulario')}
          className={`flex items-center gap-2 text-xs font-semibold px-4 py-2.5 rounded-lg transition ${
            activeSubTab === 'formulario'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-300 hover:bg-slate-700/60'
          }`}
        >
          <span>🛒</span>
          <span>Formulário de Compra (API_LINK)</span>
          {itensLista.length > 0 && (
            <span className="bg-blue-900 text-blue-200 text-[10px] px-1.5 py-0.5 rounded-full border border-blue-400/40">
              {itensLista.length} itens
            </span>
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveSubTab('planilha')}
          className={`flex items-center gap-2 text-xs font-semibold px-4 py-2.5 rounded-lg transition ${
            activeSubTab === 'planilha'
              ? 'bg-blue-600 text-white shadow'
              : 'text-slate-300 hover:bg-slate-700/60'
          }`}
        >
          <span>📥</span>
          <span>Importar Planilha Excel (.xlsx)</span>
          {comprasLote.length > 0 && (
            <span className="bg-emerald-900 text-emerald-200 text-[10px] px-1.5 py-0.5 rounded-full border border-emerald-400/40">
              {comprasLote.length} no lote
            </span>
          )}
        </button>

        <button
          type="button"
          onClick={() => setActiveSubTab('guia')}
          className={`flex items-center gap-2 text-xs font-semibold px-4 py-2.5 rounded-lg transition ${
            activeSubTab === 'guia'
              ? 'bg-indigo-600 text-white shadow'
              : 'text-slate-300 hover:bg-slate-700/60'
          }`}
        >
          <span>📖</span>
          <span>Guia do Tribunal de IA (TCU)</span>
        </button>
      </div>

      {/* Alertas de Status */}
      {statusMsg.texto && (
        <div
          className={`p-3 rounded-lg text-xs font-medium border ${
            statusMsg.tipo === 'sucesso'
              ? 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300'
              : 'bg-red-950/60 border-red-500/50 text-red-300'
          }`}
        >
          {statusMsg.texto}
        </div>
      )}

      {/* SUB-ABA 1: TRIBUNAL DA IA */}
      {activeSubTab === 'tribunal' && (
        <TribunalIA onApplyToForm={handleApplyTribunal} />
      )}

      {/* SUB-ABA 2: IMPORTADOR DE PLANILHA EM MASSA */}
      {activeSubTab === 'planilha' && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl space-y-6">
          <div className="border-b border-slate-700 pb-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <span>📥</span> Importar Planilha de Contratos e ARPs (Telebras)
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Extração automática de Processos, Contratos, Objetos, Valores, Amparos Legais e Vigências
            </p>
          </div>

          <div className="bg-slate-900/80 p-5 rounded-lg border border-slate-700 space-y-3">
            <p className="text-xs text-slate-300">
              Clique abaixo para carregar a base oficial de processos finalizados e ARPs ou buscar um contrato específico para preencher o formulário:
            </p>
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={handleProcessarPlanilha}
                disabled={loadingPlanilha}
                className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs px-5 py-2.5 rounded-lg shadow transition flex items-center gap-2"
              >
                {loadingPlanilha ? (
                  <>
                    <span className="animate-spin">⚙️</span>
                    <span>Lendo planilha e aplicando regras de extração...</span>
                  </>
                ) : (
                  <>
                    <span>⚙️</span>
                    <span>Carregar Base Oficial de Contratos (.xlsx)</span>
                  </>
                )}
              </button>

              {comprasLote.length > 0 && (
                <button
                  type="button"
                  onClick={() => setComprasLote([])}
                  className="bg-slate-700 hover:bg-slate-600 text-slate-300 text-xs px-3 py-2.5 rounded-lg transition"
                >
                  🗑️ Limpar Memória
                </button>
              )}
            </div>
          </div>

          {/* Busca e Lista de Contratos Extraídos */}
          {comprasLote.length > 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={buscaPlanilha}
                  onChange={(e) => setBuscaPlanilha(e.target.value)}
                  placeholder="Pesquisar por número do processo, contrato ou fornecedor..."
                  className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="space-y-3">
                {comprasLote
                  .filter(c =>
                    !buscaPlanilha ||
                    String(c.numero_processo || '').toLowerCase().includes(buscaPlanilha.toLowerCase()) ||
                    String(c.numero_contrato || '').toLowerCase().includes(buscaPlanilha.toLowerCase()) ||
                    String(c.fornecedor || '').toLowerCase().includes(buscaPlanilha.toLowerCase())
                  )
                  .map((item, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-900 border border-slate-700 p-4 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-600 transition"
                    >
                      <div className="space-y-1.5 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-sm">
                            {item.numero_contrato || 'Contrato S/N'}
                          </span>
                          <span className="text-xs text-slate-400 font-mono">
                            • Proc: {item.numero_processo}
                          </span>
                          <span className="text-[10px] bg-blue-900/60 text-blue-300 px-2 py-0.5 rounded border border-blue-700">
                            {item.modalidade_raw}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 line-clamp-2">
                          <strong>Objeto:</strong> {item.objeto}
                        </p>
                        <p className="text-[11px] text-slate-400">
                          <strong>Fornecedor:</strong> {item.fornecedor} ({item.cnpj_cpf}) &nbsp;|&nbsp;
                          <strong>Vigência:</strong> {item.data_inicio_estimada} até {item.data_fim_estimada}
                        </p>
                      </div>

                      <div className="flex flex-col items-end gap-2 shrink-0">
                        <span className="text-sm font-bold text-emerald-400">
                          R$ {Number(item.valor_contrato || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </span>
                        <button
                          type="button"
                          onClick={() => handlePreencherDaPlanilha(item)}
                          className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 py-2 rounded shadow transition flex items-center gap-1.5"
                        >
                          <span>📥</span>
                          <span>Preencher Formulário</span>
                        </button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* SUB-ABA 3: FORMULÁRIO OFICIAL DE COMPRA (API_LINK) */}
      {activeSubTab === 'formulario' && (
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl space-y-6">
          <div className="border-b border-slate-700 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-xl font-bold text-white flex items-center gap-2">
                <span>🛒</span> Cadastro Oficial da Compra (API_LINK)
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Estrutura oficial de campos para gravação no PLAC e publicação no PNCP
              </p>
            </div>
            <button
              type="button"
              onClick={() => setActiveSubTab('tribunal')}
              className="text-xs bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg flex items-center gap-1.5 shadow transition self-start sm:self-auto"
            >
              <span>⚖️</span>
              <span>Reavaliar com Tribunal da IA</span>
            </button>
          </div>

          <form className="space-y-6">
            {/* Bloco 1: Dados do Processo e Órgão */}
            <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-blue-400 flex items-center gap-1.5">
                <span>🏢</span> 1. Dados Básicos do Processo e Unidade
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div className="md:col-span-2">
                  <label className="block text-xs font-medium text-slate-300 mb-1">Órgão / Unidade Gestora Responsável</label>
                  <input
                    type="text"
                    disabled
                    value={formData.orgao_responsavel}
                    className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-400 text-xs font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Processo Eletrônico (PNCP)</label>
                  <input
                    type="text"
                    value={formData.link_processo_eletronico}
                    onChange={(e) => setFormData({ ...formData, link_processo_eletronico: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                    placeholder="925150 - Processo Digital"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Título / Nº do Contrato *</label>
                  <input
                    type="text"
                    value={formData.titulo}
                    onChange={(e) => setFormData({ ...formData, titulo: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                    placeholder="Ex: Contrato CTR-018/2026 ou Aquisição emergencial..."
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Número do Processo SEI/SIGA *</label>
                  <input
                    type="text"
                    value={formData.numero_processo}
                    onChange={(e) => setFormData({ ...formData, numero_processo: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                    placeholder="Ex: 53000.002814/2026-31"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Justificativa de Não Ser Planejada (Contratação Extraordinária)
                </label>
                <textarea
                  rows="2"
                  value={formData.justificativa_nao_planejada}
                  onChange={(e) => setFormData({ ...formData, justificativa_nao_planejada: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  placeholder="Se a contratação for fora do ciclo anual ordinário do PLAC, descreva a necessidade superveniente..."
                />
              </div>
            </div>

            {/* Bloco 2: Enquadramento e Amparo Legal */}
            <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <span>⚖️</span> 2. Modalidade e Fundamentação Legal (Amparo PNCP)
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Modalidade de Contratação *</label>
                  <select
                    value={formData.modalidade_id}
                    onChange={(e) => {
                      const id = parseInt(e.target.value);
                      const modMap = { 8: 'Dispensa de Licitação', 9: 'Inexigibilidade de Licitação', 10: 'Credenciamento', 6: 'Pregão Eletrônico' };
                      setFormData({ ...formData, modalidade_id: id, modalidade_nome: modMap[id] });
                    }}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  >
                    <option value={8}>Dispensa de Licitação (ID 8)</option>
                    <option value={9}>Inexigibilidade de Licitação (ID 9)</option>
                    <option value={10}>Credenciamento (ID 10)</option>
                    <option value={6}>Pregão Eletrônico (ID 6)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Modo de Disputa</label>
                  <select
                    value={formData.modo_disputa}
                    onChange={(e) => setFormData({ ...formData, modo_disputa: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  >
                    <option value="Não se aplica">Não se aplica</option>
                    <option value="Dispensa com Disputa">Dispensa com Disputa</option>
                    <option value="Aberto/Fechado">Aberto/Fechado</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Categoria do Objeto</label>
                  <select
                    value={formData.categoria}
                    onChange={(e) => setFormData({ ...formData, categoria: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  >
                    <option value="Serviços">Serviços</option>
                    <option value="Bens">Bens / Materiais</option>
                    <option value="Serviços Contínuos">Serviços Contínuos</option>
                    <option value="Obras e Engenharia">Obras e Engenharia</option>
                    <option value="TI">Tecnologia da Informação</option>
                  </select>
                </div>
              </div>

              {/* Seletor de Amparo Legal com Detalhe */}
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Amparo Legal Selecionado (Lei, Artigo e Inciso PNCP) *
                </label>
                <select
                  value={formData.amparo_legal_id}
                  onChange={(e) => {
                    const id = parseInt(e.target.value);
                    setFormData({ ...formData, amparo_legal_id: id });
                    const amparo = amparosDisponiveis.find(a => a.id === id);
                    if (amparo) setAmparoSelecionadoDetalhe(amparo);
                  }}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs font-mono"
                >
                  {amparosDisponiveis.map(amp => (
                    <option key={amp.id} value={amp.id}>
                      [{amp.lei}] Art. {amp.artigo}, Inc. {amp.inciso} — {amp.nome}
                    </option>
                  ))}
                </select>

                {amparoSelecionadoDetalhe && (
                  <div className="mt-2 p-2.5 bg-slate-950/70 border border-slate-800 rounded text-xs space-y-1">
                    <p className="text-slate-400 font-semibold">Texto Oficial do Amparo:</p>
                    <p className="text-slate-300 italic font-serif">"{amparoSelecionadoDetalhe.descricao}"</p>
                  </div>
                )}
              </div>
            </div>

            {/* Bloco 3: Prazos, Vigência e Objeto */}
            <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-4">
              <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
                <span>📅</span> 3. Prazos, Vigência e Descrição do Objeto
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Data Estimada de Início *</label>
                  <input
                    type="date"
                    value={formData.data_inicio}
                    onChange={(e) => setFormData({ ...formData, data_inicio: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Data Estimada de Fim *</label>
                  <input
                    type="date"
                    value={formData.data_fim}
                    onChange={(e) => setFormData({ ...formData, data_fim: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Descrição Sucinta do Objeto (PNCP) *</label>
                <textarea
                  rows="3"
                  value={formData.objeto}
                  onChange={(e) => setFormData({ ...formData, objeto: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  placeholder="Descrição completa no padrão técnico do PNCP..."
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Informações Complementares (Fornecedor, CNPJ, etc.)</label>
                <textarea
                  rows="2"
                  value={formData.informacoes_complementares}
                  onChange={(e) => setFormData({ ...formData, informacoes_complementares: e.target.value })}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-xs"
                  placeholder="Dados do fornecedor exclusivo, pareceres de auditoria ou notas fiscais anteriores..."
                />
              </div>
            </div>

            {/* Bloco 4: Itens de Contratação (CATMAT/CATSER) */}
            <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-4">
              <div className="flex items-center justify-between border-b border-slate-700 pb-2">
                <h3 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                  <span>📋</span> 4. Itens de Contratação (Bens e Serviços)
                </h3>
                <span className="text-xs font-bold text-emerald-400">
                  Total da Compra: R$ {valorTotalGeral.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                </span>
              </div>

              {/* Tabela de Itens Adicionados */}
              {itensLista.length === 0 ? (
                <p className="text-xs text-slate-400 italic">Nenhum item adicionado à compra ainda.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left text-slate-300">
                    <thead className="bg-slate-800 text-slate-400 uppercase text-[10px]">
                      <tr>
                        <th className="p-2">Item</th>
                        <th className="p-2">Tipo</th>
                        <th className="p-2">Código</th>
                        <th className="p-2">Descrição</th>
                        <th className="p-2 text-right">Qtd</th>
                        <th className="p-2">Und</th>
                        <th className="p-2 text-right">Unitário (R$)</th>
                        <th className="p-2 text-right">Total (R$)</th>
                        <th className="p-2 text-center">Ações</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                      {itensLista.map((it, idx) => (
                        <tr key={idx} className="hover:bg-slate-850">
                          <td className="p-2 font-bold">{idx + 1}</td>
                          <td className="p-2">
                            <span className={`px-1.5 py-0.5 rounded text-[10px] ${it.tipo === 'S' ? 'bg-purple-900 text-purple-300' : 'bg-blue-900 text-blue-300'}`}>
                              {it.tipo === 'S' ? 'Serviço' : 'Material'}
                            </span>
                          </td>
                          <td className="p-2 font-mono text-[11px]">{it.codigo || it.catalogoCodigoItem || '0000'}</td>
                          <td className="p-2 max-w-xs truncate">{it.descricao}</td>
                          <td className="p-2 text-right font-mono">{it.quantidade}</td>
                          <td className="p-2">{it.unidadeMedida || it.unidade || 'UN'}</td>
                          <td className="p-2 text-right font-mono">
                            {Number(it.valorUnitarioEstimado || it.valor_unitario || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </td>
                          <td className="p-2 text-right font-bold text-emerald-400 font-mono">
                            {Number(it.valorTotal || it.valor_total || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                          </td>
                          <td className="p-2 text-center">
                            <button
                              type="button"
                              onClick={() => handleRemoveItem(idx)}
                              className="text-red-400 hover:text-red-300 px-1.5 py-0.5 rounded transition text-xs"
                            >
                              🗑️
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Formulário de Adição Rápida de Item */}
              <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 space-y-3">
                <p className="text-[11px] font-bold text-slate-400 uppercase">➕ Adicionar Item ao Processo:</p>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-2">
                  <div className="md:col-span-2">
                    <label className="block text-[10px] text-slate-400 mb-1">Descrição Oficial do Item</label>
                    <input
                      type="text"
                      value={novoItem.descricao}
                      onChange={(e) => setNovoItem({ ...novoItem, descricao: e.target.value })}
                      placeholder="Ex: Suporte técnico de banco de dados..."
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-white text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 mb-1">Tipo</label>
                    <select
                      value={novoItem.tipo}
                      onChange={(e) => setNovoItem({ ...novoItem, tipo: e.target.value })}
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-white text-xs"
                    >
                      <option value="S">Serviço</option>
                      <option value="M">Material</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 mb-1">Unidade</label>
                    <select
                      value={novoItem.unidade}
                      onChange={(e) => setNovoItem({ ...novoItem, unidade: e.target.value })}
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-white text-xs"
                    >
                      <option value="MÊS">MÊS</option>
                      <option value="UN">UN (Unidade)</option>
                      <option value="SV">SV (Serviço)</option>
                      <option value="LOTE">LOTE</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                  <div>
                    <label className="block text-[10px] text-slate-400 mb-1">Quantidade / Parcelas</label>
                    <input
                      type="number"
                      step="1"
                      min="1"
                      value={novoItem.quantidade}
                      onChange={(e) => setNovoItem({ ...novoItem, quantidade: e.target.value })}
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-white text-xs"
                    />
                  </div>
                  <div>
                    <label className="block text-[10px] text-slate-400 mb-1">Valor Unitário / Parcela (R$)</label>
                    <input
                      type="number"
                      step="0.01"
                      min="0"
                      value={novoItem.valor_unitario}
                      onChange={(e) => setNovoItem({ ...novoItem, valor_unitario: e.target.value })}
                      className="w-full px-2.5 py-1.5 bg-slate-900 border border-slate-700 rounded text-white text-xs"
                    />
                  </div>
                  <div className="flex items-end">
                    <button
                      type="button"
                      onClick={handleAddItem}
                      className="w-full bg-slate-800 hover:bg-slate-700 text-blue-300 border border-blue-500/40 text-xs font-bold py-1.5 rounded transition"
                    >
                      ➕ Incluir Item
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Ações de Finalização */}
            <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-slate-700">
              <button
                type="button"
                onClick={handleSalvarCompra}
                disabled={isSubmitting}
                className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs px-6 py-3 rounded-lg shadow-lg flex items-center justify-center gap-2 transition"
              >
                {isSubmitting ? (
                  <>
                    <span className="animate-spin">⚙️</span>
                    <span>Salvando contratação no PLAC...</span>
                  </>
                ) : (
                  <>
                    <span>💾</span>
                    <span>Salvar na Gestão de Demandas (PLAC)</span>
                  </>
                )}
              </button>

              <button
                type="button"
                onClick={() => {
                  setStatusMsg({
                    tipo: 'sucesso',
                    texto: '🌐 Simulação concluída! Dados validados de acordo com o esquema da API do PNCP para UASG 925150.'
                  });
                }}
                className="bg-emerald-700 hover:bg-emerald-600 text-white font-bold text-xs px-5 py-3 rounded-lg shadow transition flex items-center justify-center gap-2"
              >
                <span>🌐</span>
                <span>Simular Envio ao PNCP</span>
              </button>
            </div>
          </form>
        </div>
      )}

      {/* SUB-ABA 4: GUIA DIDÁTICO DO TRIBUNAL DA IA */}
      {activeSubTab === 'guia' && (
        <GuiaTribunalIA />
      )}
    </div>
  );
}
