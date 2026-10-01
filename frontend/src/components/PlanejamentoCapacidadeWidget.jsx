import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function PlanejamentoCapacidadeWidget({ onSelectData, initialModalidade = 'PREGAO', initialData = '' }) {
  const [modalidade, setModalidade] = useState(initialModalidade);
  const [dataPretendida, setDataPretendida] = useState(() => {
    if (initialData) return initialData;
    // Padrão: 8 meses à frente para dar folga de rito
    const d = new Date();
    d.setMonth(d.getMonth() + 8);
    return d.toISOString().split('T')[0];
  });

  const [loading, setLoading] = useState(false);
  const [cronograma, setCronograma] = useState(null);
  const [capacidade, setCapacidade] = useState(null);
  const [janelas, setJanelas] = useState([]);
  const [showJanelas, setShowJanelas] = useState(false);

  const modalidadesList = [
    { grupo: 'Licitação Geral (Lei 13.303/2016)', items: [
      { id: 'PREGAO', nome: 'Pregão Eletrônico (Licitação Ampla)', sla: '31 d.u. (Média Real / IC 99%)', folga: '144 d.u.' }
    ]},
    { grupo: 'Dispensas de Licitação (Art. 29)', items: [
      { id: 'DISPENSA_TRADICIONAL', nome: 'Dispensa Tradicional Geral', sla: '15 d.u. (Média Real / IC 99%)', folga: '59 d.u.' },
      { id: 'DISPENSA_BAIXO_VALOR', nome: 'Dispensa Tradicional Baixo Valor (Inc. I e II)', sla: '11 d.u. (Média Real / IC 99%)', folga: '37 d.u.' },
      { id: 'DISPENSA_ELETRONICA', nome: 'Dispensa Eletrônica Comprasnet (IN 67/2021)', sla: '15 d.u. (Média Real / IC 99%)', folga: '45 d.u.' },
      { id: 'DISPENSA_LOCACAO', nome: 'Dispensa para Locação de Imóveis/PoPs (Parecer Padrão)', sla: '20 d.u. (Média Real / IC 99%)', folga: '52 d.u.' },
      { id: 'DISPENSA_ENERGIA', nome: 'Dispensa para Energia Elétrica (Parecer Padrão)', sla: '17 d.u. (Média Real / IC 99%)', folga: '48 d.u.' }
    ]},
    { grupo: 'Inexigibilidades (Art. 30)', items: [
      { id: 'INEXIGIBILIDADE_GERAL', nome: 'Inexigibilidade Geral / Fornecedor Exclusivo', sla: '25 d.u. (Média Real / IC 99%)', folga: '65 d.u.' },
      { id: 'INEXIGIBILIDADE_CURSOS', nome: 'Inexigibilidade Cursos e Treinamentos (Parecer Padrão)', sla: '9 d.u. (Média Real / IC 99%)', folga: '22 d.u.' },
      { id: 'INEXIGIBILIDADE_COMPARTILHAMENTO', nome: 'Inexigibilidade Compartilhamento de Infraestrutura', sla: '28 d.u. (Média Real / IC 99%)', folga: '72 d.u.' }
    ]},
    { grupo: 'Oportunidade Comercial', items: [
      { id: 'AFASTAMENTO', nome: 'Afastamento de Licitação (Prática nº 88 / Art. 28)', sla: '26 d.u. (Média Real / IC 99%)', folga: '60 d.u.' }
    ]}
  ];

  const carregarDiagnostico = async () => {
    if (!dataPretendida) return;
    try {
      setLoading(true);
      const [resCrono, resCap, resJan] = await Promise.all([
        api.post('/planejamento/cronograma-reverso/', {
          modalidade: modalidade,
          data_pretendida_assinatura: dataPretendida
        }),
        api.get(`/planejamento/verificar-capacidade/?data=${dataPretendida}&modalidade=${modalidade}`),
        api.get(`/planejamento/janelas-cabiveis/?modalidade=${modalidade}&quantidade=3`)
      ]);

      setCronograma(resCrono.data);
      setCapacidade(resCap.data);
      setJanelas(resJan.data.janelas_cabiveis || []);
    } catch (err) {
      console.error('Erro ao carregar capacidade e cronograma reverso:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    carregarDiagnostico();
  }, [modalidade, dataPretendida]);

  const aplicarDataSugerida = (novaData) => {
    setDataPretendida(novaData);
    if (onSelectData) {
      onSelectData(novaData);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-xl text-slate-200 space-y-5">
      {/* Cabeçalho do Widget */}
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-600 to-indigo-600 flex items-center justify-center text-xl shadow-lg shadow-amber-500/20">
            🤖
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Robô de Gestão de Planejamento & Capacidade GCC
              <span className="text-[10px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 px-2 py-0.5 rounded font-mono">
                Agendamento Inteligente
              </span>
            </h3>
            <p className="text-xs text-slate-400">
              Cálculo reverso de datas regimentais da Telebras e balizamento de sobrecarga operacional da esteira.
            </p>
          </div>
        </div>

        {cronograma && (
          <div className={`px-3 py-1.5 rounded-xl border flex items-center gap-2 text-xs font-bold font-mono ${
            cronograma.cor_semaforo === 'VERDE'
              ? 'bg-emerald-950/80 border-emerald-500/50 text-emerald-300'
              : cronograma.cor_semaforo === 'AMARELO'
              ? 'bg-amber-950/80 border-amber-500/50 text-amber-300'
              : 'bg-rose-950/80 border-rose-500/50 text-rose-300 animate-pulse'
          }`}>
            <span className={`w-2.5 h-2.5 rounded-full ${
              cronograma.cor_semaforo === 'VERDE' ? 'bg-emerald-400' : cronograma.cor_semaforo === 'AMARELO' ? 'bg-amber-400' : 'bg-rose-500'
            }`} />
            {cronograma.status_viabilidade} ({cronograma.classificacao_risco})
          </div>
        )}
      </div>

      {/* Seletor de Modalidade e Data Pretendida */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">
            Modalidade / Esteira da GCC (10 Modalidades Oficiais)
          </label>
          <select
            value={modalidade}
            onChange={(e) => setModalidade(e.target.value)}
            className="w-full bg-slate-950 border border-slate-750 text-white rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none"
          >
            {modalidadesList.map((grp, idx) => (
              <optgroup key={idx} label={grp.grupo} className="bg-slate-900 text-slate-300 font-bold">
                {grp.items.map((it) => (
                  <option key={it.id} value={it.id} className="bg-slate-950 text-white font-normal">
                    {it.nome} — [SLA: {it.sla}]
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center justify-between">
            <span>Data Pretendida de Homologação / Assinatura</span>
            {cronograma && (
              <span className="text-[11px] font-mono text-amber-400 font-bold">
                {cronograma.quadrimestre_alvo}
              </span>
            )}
          </label>
          <input
            type="date"
            value={dataPretendida}
            onChange={(e) => setDataPretendida(e.target.value)}
            className="w-full bg-slate-950 border border-slate-750 text-white rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500 outline-none font-mono"
          />
        </div>
      </div>

      {/* Banner de Risco de Urgência Retroativa */}
      {cronograma && cronograma.eh_retroativo && (
        <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/60 text-rose-200 text-xs space-y-2">
          <div className="flex items-center gap-2 font-bold text-rose-300 text-sm">
            <span>🚨</span>
            <span>ALERTA DE DESCONFORMIDADE: URGÊNCIA FABRICADA</span>
          </div>
          <p className="leading-relaxed">
            {cronograma.recomendacao_planejamento}
          </p>
          <div className="flex items-center gap-2 pt-1 font-mono text-[11px] text-rose-400">
            <span>Atraso acumulado: <strong>{cronograma.dias_em_atraso} dias</strong></span>
            <span>•</span>
            <span>Rito oficial da GCC: <strong>{cronograma.sla_regimental_gcc_dias_uteis} dias úteis</strong></span>
          </div>
        </div>
      )}

      {/* Régua Visual do Cronograma Reverso */}
      {cronograma && (
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-300 flex items-center gap-1.5">
              <span>📅</span> Cronograma Reverso Regimental (Lei 13.303/2016 e RILC Telebras)
            </span>
            <span className="text-slate-400 font-mono text-[11px]">
              Total: <strong>{cronograma.total_dias_uteis_necessarios} dias úteis</strong>
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
            {/* Marco 1: Abertura SIGA */}
            <div className={`p-3 rounded-lg border flex flex-col justify-between ${
              cronograma.eh_retroativo
                ? 'bg-rose-950/30 border-rose-500/40'
                : 'bg-indigo-950/30 border-indigo-500/30'
            }`}>
              <div>
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">
                  1. Data Fatal Abertura SIGA
                </span>
                <span className="text-sm font-bold font-mono text-white block mt-0.5">
                  {cronograma.data_fatal_abertura_siga.split('-').reverse().join('/')}
                </span>
              </div>
              <p className="text-[10px] text-slate-400 mt-2">
                Área emite a <strong>Certidão do PLAC</strong> e autua o processo no SIGA.
              </p>
            </div>

            {/* Marco 2: Envio à GCC */}
            <div className="p-3 rounded-lg border bg-slate-900 border-slate-750 flex flex-col justify-between">
              <div>
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">
                  2. Data-Limite Envio à GCC
                </span>
                <span className="text-sm font-bold font-mono text-amber-300 block mt-0.5">
                  {cronograma.data_limite_envio_gcc.split('-').reverse().join('/')}
                </span>
              </div>
              <p className="text-[10px] text-slate-400 mt-2">
                ETP/TR saneado e aprovação da Diretoria protocolados na GCC.
              </p>
            </div>

            {/* Marco 3: Homologação / Assinatura */}
            <div className="p-3 rounded-lg border bg-emerald-950/30 border-emerald-500/30 flex flex-col justify-between">
              <div>
                <span className="text-[10px] text-slate-400 font-mono uppercase tracking-wider block">
                  3. Assinatura / Homologação
                </span>
                <span className="text-sm font-bold font-mono text-emerald-300 block mt-0.5">
                  {cronograma.data_pretendida_assinatura.split('-').reverse().join('/')}
                </span>
              </div>
              <p className="text-[10px] text-slate-400 mt-2">
                Conclusão do certame e publicação no DOU e PNCP.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Motor Estatístico de Inferência Realista (Opção B: IC 99% / Margem <= 2%) */}
      {cronograma && cronograma.cenarios && (
        <div className="bg-slate-950/80 border border-indigo-500/40 rounded-xl p-4 space-y-3.5 shadow-lg">
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-2.5">
            <div className="flex items-center gap-2">
              <span className="text-lg">📊</span>
              <div>
                <h4 className="text-xs font-bold text-white flex items-center gap-2">
                  Motor de Inferência Estatística Amostral
                  <span className="bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 px-2 py-0.5 rounded text-[10px] font-mono">
                    IC 99% (Z = {cronograma.z_score})
                  </span>
                  <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-2 py-0.5 rounded text-[10px] font-mono">
                    Margem: {cronograma.margem_erro_pct}%
                  </span>
                </h4>
                <p className="text-[11px] text-slate-400">
                  Previsão realista eliminando os <strong>{cronograma.prazo_planilha_antigo_gcc} dias de folga</strong> da planilha antiga.
                </p>
              </div>
            </div>

            {cronograma.ganho_eficiencia_folga_dias > 0 && (
              <span className="text-[11px] font-mono font-bold text-emerald-400 bg-emerald-950/80 border border-emerald-500/40 px-2.5 py-1 rounded-lg">
                ⚡ Economia de {cronograma.ganho_eficiencia_folga_dias} dias úteis
              </span>
            )}
          </div>

          {/* Os 3 Cenários (Otimista, Esperado, Pessimista) */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {/* Cenário Otimista */}
            <div className="p-3 rounded-lg border bg-emerald-950/20 border-emerald-500/30 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold text-emerald-400">
                  <span>🟢 Cenário Otimista</span>
                  <span>{cronograma.cenarios.otimista.dias_tramitacao_gcc} d.u. (GCC)</span>
                </div>
                <div className="mt-2 text-white font-mono text-sm font-extrabold">
                  {cronograma.cenarios.otimista.data_prevista_formatada}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">
                  Lead time total: <strong>{cronograma.cenarios.otimista.lead_time_total_local} dias úteis</strong>
                </div>
              </div>
              <p className="text-[10px] text-slate-400 mt-2 italic">
                {cronograma.cenarios.otimista.descricao}
              </p>
            </div>

            {/* Cenário Esperado (Média) */}
            <div className="p-3 rounded-lg border bg-blue-950/20 border-blue-500/40 flex flex-col justify-between ring-1 ring-blue-500/30">
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold text-blue-400">
                  <span>🔵 Cenário Esperado (Média)</span>
                  <span>{cronograma.cenarios.esperado.dias_tramitacao_gcc} d.u. (GCC)</span>
                </div>
                <div className="mt-2 text-white font-mono text-sm font-extrabold">
                  {cronograma.cenarios.esperado.data_prevista_formatada}
                </div>
                <div className="text-[10px] text-slate-300 mt-1">
                  Lead time total: <strong>{cronograma.cenarios.esperado.lead_time_total_local} dias úteis</strong>
                </div>
              </div>
              <p className="text-[10px] text-slate-400 mt-2 italic">
                {cronograma.cenarios.esperado.descricao}
              </p>
            </div>

            {/* Cenário Pessimista (P99) */}
            <div className="p-3 rounded-lg border bg-purple-950/20 border-purple-500/30 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between text-[11px] font-bold text-purple-400">
                  <span>🔴 Cenário Pessimista (P99)</span>
                  <span>{cronograma.cenarios.pessimista.dias_tramitacao_gcc} d.u. (GCC)</span>
                </div>
                <div className="mt-2 text-white font-mono text-sm font-extrabold">
                  {cronograma.cenarios.pessimista.data_prevista_formatada}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">
                  Lead time total: <strong>{cronograma.cenarios.pessimista.lead_time_total_local} dias úteis</strong>
                </div>
              </div>
              <p className="text-[10px] text-slate-400 mt-2 italic">
                {cronograma.cenarios.pessimista.descricao}
              </p>
            </div>
          </div>

          {/* Caixa de Diagnóstico da Chegada no Local */}
          {cronograma.previsao_entrega_local && (
            <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 text-[11px] text-slate-300 flex items-start gap-2.5">
              <span className="text-base">📦</span>
              <div>
                <strong className="text-white">Previsão Real de Chegada do Material / Início do Serviço no Local:</strong>
                <p className="text-slate-400 mt-0.5 leading-relaxed">
                  {cronograma.previsao_entrega_local.diagnostico_comparativo}
                </p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Monitor de Capacidade Operacional da GCC */}
      {capacidade && (
        <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between text-xs">
            <span className="font-bold text-slate-300 flex items-center gap-1.5">
              <span>⚖️</span> Capacidade Operacional da Equipe de Compras (GCC)
            </span>
            <span className={`text-[11px] font-bold px-2 py-0.5 rounded font-mono ${
              capacidade.cor_capacidade === 'VERDE'
                ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40'
                : capacidade.cor_capacidade === 'AMARELO'
                ? 'bg-amber-950 text-amber-400 border border-amber-500/40'
                : 'bg-rose-950 text-rose-400 border border-rose-500/40'
            }`}>
              {capacidade.total_certames_janela} de {capacidade.limiar_maximo_simultaneo} Certames ({capacidade.taxa_ocupacao_pct}%)
            </span>
          </div>

          {/* Barra de Progresso de Ocupação da GCC */}
          <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                capacidade.taxa_ocupacao_pct < 60
                  ? 'bg-emerald-500'
                  : capacidade.taxa_ocupacao_pct <= 100
                  ? 'bg-amber-500'
                  : 'bg-rose-500'
              }`}
              style={{ width: `${Math.min(100, capacidade.taxa_ocupacao_pct)}%` }}
            />
          </div>

          <p className="text-xs text-slate-400">
            {capacidade.mensagem_capacidade}
          </p>
        </div>
      )}

      {/* Sugestão Autônoma de Janelas Cabíveis */}
      <div className="border border-slate-800 rounded-xl overflow-hidden">
        <button
          type="button"
          onClick={() => setShowJanelas(!showJanelas)}
          className="w-full bg-slate-850 hover:bg-slate-800 px-4 py-3 flex items-center justify-between text-xs font-bold text-white transition"
        >
          <div className="flex items-center gap-2">
            <span>✨</span>
            <span>Ver Janelas Cabíveis Recomendadas no Calendário ({janelas.length} opções disponíveis)</span>
          </div>
          <span className="text-slate-400 text-xs">{showJanelas ? '▲ Recolher' : '▼ Expandir'}</span>
        </button>

        {showJanelas && (
          <div className="p-4 bg-slate-950 space-y-3">
            <p className="text-xs text-slate-400">
              O Robô de Planejamento analisou a esteira e encontrou os seguintes slots ideais que respeitam integralmente os prazos da GCC:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {janelas.map((j, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl border border-slate-800 bg-slate-900/90 flex flex-col justify-between hover:border-amber-500/50 transition group space-y-2.5"
                >
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-white font-mono">
                        {j.data_formatada}
                      </span>
                      <span className="text-[10px] bg-indigo-900/80 text-indigo-300 font-bold px-1.5 py-0.5 rounded font-mono">
                        {j.quadrimestre}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400">
                      Autuação no SIGA até: <strong className="text-slate-200">{j.data_fatal_abertura_siga.split('-').reverse().join('/')}</strong>
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() => aplicarDataSugerida(j.data_sugerida_assinatura)}
                    className="w-full py-1.5 px-2 bg-amber-500 hover:bg-amber-400 text-black font-extrabold text-[11px] rounded-lg transition shadow-md shadow-amber-500/20"
                  >
                    Adotar Esta Janela
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
