import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';
import CertidaoVinculacaoModal from './CertidaoVinculacaoModal';

export default function PlanejamentoEsteiraKanban() {
  const [quadrimestre, setQuadrimestre] = useState('TODOS');
  const [ano, setAno] = useState(2026);
  const [loading, setLoading] = useState(true);
  const [resumo, setResumo] = useState(null);
  const [colunas, setColunas] = useState({
    levantamento: [],
    validacao_diretor: [],
    consolidacao_gcc: [],
    deliberacao_redir: [],
    calendario_vigente: [],
    devolvido_ajustes: [],
  });

  const [selectedDemandForCertidao, setSelectedDemandForCertidao] = useState(null);
  const [devolverTarget, setDevolverTarget] = useState(null);
  const [motivoDevolucao, setMotivoDevolucao] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [feedback, setFeedback] = useState(null);

  // Ref para controle suave da rolagem horizontal do Kanban
  const kanbanScrollRef = useRef(null);

  const scrollKanban = (direction) => {
    if (kanbanScrollRef.current) {
      // Rola aproximadamente a largura de uma a duas colunas
      const scrollAmount = kanbanScrollRef.current.clientWidth * 0.7;
      kanbanScrollRef.current.scrollBy({ left: direction * scrollAmount, behavior: 'smooth' });
    }
  };

  const scrollToFase = (fase) => {
    if (kanbanScrollRef.current) {
      if (fase === 'inicio') {
        kanbanScrollRef.current.scrollTo({ left: 0, behavior: 'smooth' });
      } else if (fase === 'deliberacao') {
        kanbanScrollRef.current.scrollTo({ left: kanbanScrollRef.current.scrollWidth, behavior: 'smooth' });
      }
    }
  };

  const fetchKanban = async () => {
    try {
      setLoading(true);
      const params = {};
      if (quadrimestre !== 'TODOS') params.quadrimestre = quadrimestre;
      if (ano) params.ano = ano;

      const res = await api.get('/demands/esteira_kanban/', { params });
      setResumo(res.data.resumo);
      setColunas(res.data.colunas);
    } catch (err) {
      console.error('Erro ao carregar esteira kanban:', err);
      showFeedback('Erro ao sincronizar esteira de planejamento.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchKanban();
  }, [quadrimestre, ano]);

  const showFeedback = (msg, type = 'success') => {
    setFeedback({ msg, type });
    setTimeout(() => setFeedback(null), 6000);
  };

  const handleAvancarFase = async (demand) => {
    // Trava de Governança no Frontend: alertar imediatamente se tentar avançar sem SIGA
    if (!demand.siga_process_number) {
      showFeedback(
        `⛔ Bloqueio de Governança: A demanda ${demand.codigo_rastreio_plac || '#' + demand.id} deve ter o processo SIGA autuado com a Certidão do PLAC como Peça nº 01 antes do julgamento da Diretoria.`,
        'error'
      );
      setSelectedDemandForCertidao(demand);
      return;
    }

    try {
      setActionLoading(true);
      await api.post(`/demands/${demand.id}/avancar_fase/`);
      showFeedback(`Demanda ${demand.codigo_rastreio_plac || '#' + demand.id} avançou com sucesso no ciclo de planejamento!`);
      fetchKanban();
    } catch (err) {
      const errMsg = err.response?.data?.error || 'Erro ao avançar fase da demanda.';
      showFeedback(errMsg, 'error');
      if (err.response?.data?.bloqueio_siga) {
        setSelectedDemandForCertidao(demand);
      }
    } finally {
      setActionLoading(false);
    }
  };

  const handleConfirmDevolver = async () => {
    if (!devolverTarget) return;
    if (!motivoDevolucao.trim()) {
      alert('Informe a justificativa/motivo para devolução da demanda.');
      return;
    }

    try {
      setActionLoading(true);
      await api.post(`/demands/${devolverTarget.id}/retroceder_fase/`, {
        motivo: motivoDevolucao.trim()
      });
      showFeedback(`Demanda #${devolverTarget.id} devolvida para ajustes com sucesso.`, 'info');
      setDevolverTarget(null);
      setMotivoDevolucao('');
      fetchKanban();
    } catch (err) {
      showFeedback('Erro ao devolver demanda para ajustes.', 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const handleDownloadMinutaPdf = async () => {
    try {
      const qParam = quadrimestre !== 'TODOS' ? quadrimestre : '';
      const res = await api.get('/planejamento/minuta-consolidada-pdf/', {
        params: { quadrimestre: qParam, ano },
        responseType: 'blob'
      });

      const blob = new Blob([res.data], { type: 'application/pdf' });
      const link = document.createElement('a');
      link.href = window.URL.createObjectURL(blob);
      link.download = `Minuta_Consolidada_PLAC_${ano}_${quadrimestre}.pdf`;
      link.click();
      window.URL.revokeObjectURL(link.href);
      showFeedback('Minuta Consolidada baixada com sucesso!');
    } catch (err) {
      console.error(err);
      showFeedback('Erro ao gerar Minuta Consolidada em PDF.', 'error');
    }
  };

  const formatBRL = (val) => {
    return Number(val || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  // Cores do Semáforo da GCC com tratamento robusto para valores nulos
  const getSemaforoGCC = () => {
    if (!resumo || !resumo.capacidade_gcc) return { cor: 'slate', texto: 'Apurando...', desc: 'Apurando capacidade...', bg: 'bg-slate-800 border-slate-700 text-slate-300', badge: '⏳ Apurando' };
    const totalProcessos = resumo.capacidade_gcc.total_processos_mes ?? resumo.capacidade_gcc.total ?? 0;
    const statusCap = resumo.capacidade_gcc.status;
    if (statusCap === 'VERDE') {
      return {
        cor: 'emerald',
        bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
        badge: '🟢 Fluxo Normal',
        desc: `${totalProcessos} certames simultâneos (abaixo do limiar de 6)`
      };
    } else if (statusCap === 'AMARELO') {
      return {
        cor: 'amber',
        bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
        badge: '🟡 Atenção / Carga Moderada',
        desc: `${totalProcessos} certames simultâneos (faixa de atenção 6 a 8)`
      };
    } else {
      return {
        cor: 'rose',
        bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
        badge: '🔴 Sobrecarga Crítica GCC',
        desc: `${totalProcessos} certames previstos (excede limiar de 8)! Recomenda-se redistribuição.`
      };
    }
  };

  const semaforo = getSemaforoGCC();

  return (
    <div className="space-y-6">
      {/* Toast Feedback */}
      {feedback && (
        <div
          className={`p-4 rounded-xl flex items-center justify-between shadow-lg text-sm border font-medium ${
            feedback.type === 'error'
              ? 'bg-rose-950/90 border-rose-700 text-rose-200'
              : feedback.type === 'info'
              ? 'bg-amber-950/90 border-amber-700 text-amber-200'
              : 'bg-emerald-950/90 border-emerald-700 text-emerald-200'
          }`}
        >
          <div className="flex items-center gap-2">
            <span>{feedback.type === 'error' ? '⚠️' : '✅'}</span>
            <span>{feedback.msg}</span>
          </div>
          <button onClick={() => setFeedback(null)} className="text-xs opacity-70 hover:opacity-100">✕</button>
        </div>
      )}

      {/* Cabeçalho da Esteira e Filtro por Quadrimestre */}
      <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-6 shadow-xl backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="text-2xl">🏛️</span>
              <h2 className="text-xl font-bold text-white tracking-tight">
                Esteira de Governança do Planejamento PLAC
              </h2>
              <span className="bg-blue-600/20 text-blue-400 text-xs px-2.5 py-0.5 rounded-full border border-blue-500/30 font-semibold">
                Funil Oficial Telebras
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Rito regimental: <span className="text-slate-300 font-medium">1. Levantamento</span> ➔{' '}
              <span className="text-slate-300 font-medium">2. Validação Diretoria</span> (com Amarração SIGA) ➔{' '}
              <span className="text-slate-300 font-medium">3. Consolidação GCC</span> ➔{' '}
              <span className="text-slate-300 font-medium">4. Deliberação REDIR</span> ➔{' '}
              <span className="text-slate-300 font-medium">5. Calendário Anual Vigente</span>.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            {/* Seletor de Quadrimestre */}
            <div className="bg-slate-900/90 p-1 rounded-xl border border-slate-700 flex items-center gap-1">
              {[
                { id: 'TODOS', label: 'Todos' },
                { id: 'Q1', label: 'Q1 (Jan-Abr)' },
                { id: 'Q2', label: 'Q2 (Mai-Ago)' },
                { id: 'Q3', label: 'Q3 (Set-Dez)' },
              ].map((q) => (
                <button
                  key={q.id}
                  onClick={() => setQuadrimestre(q.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    quadrimestre === q.id
                      ? 'bg-blue-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  {q.label}
                </button>
              ))}
            </div>

            {/* Botão de Emissão de Minuta Consolidada REDIR */}
            <button
              onClick={handleDownloadMinutaPdf}
              className="flex items-center gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold px-4 py-2 rounded-xl shadow-md transition"
              title="Gera PDF oficial consolidado para instrução da Ata da REDIR"
            >
              <span>📑</span>
              <span>Minuta Consolidada REDIR</span>
            </button>
          </div>
        </div>

        {/* Barra de Cards Analíticos de Governança */}
        {resumo && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6 pt-6 border-t border-slate-700/60">
            {/* Card 1: Orçamento e Volume */}
            <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                Volume no {quadrimestre === 'TODOS' ? 'Exercício' : quadrimestre}
              </div>
              <div className="text-xl font-bold text-white mt-1">
                {resumo.total_demandas} demandas
              </div>
              <div className="text-xs text-blue-400 font-semibold mt-0.5">
                {formatBRL(resumo.orcamento_total)}
              </div>
            </div>

            {/* Card 2: Semáforo GCC */}
            <div className={`border rounded-xl p-4 ${semaforo.bg}`}>
              <div className="text-[11px] font-semibold uppercase tracking-wider flex items-center justify-between">
                <span>Capacidade GCC</span>
                <span className="text-[10px] font-bold">{semaforo.badge}</span>
              </div>
              <div className="text-sm font-bold mt-1">
                {semaforo.desc}
              </div>
              <div className="text-[10px] opacity-80 mt-1">
                Limiar seguro: até 8 certames simultâneos
              </div>
            </div>

            {/* Card 3: Amarração SIGA */}
            <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span>Conformidade SIGA</span>
                <span className="text-xs">🔗</span>
              </div>
              <div className="text-xl font-bold text-white mt-1">
                {resumo.total_demandas - resumo.sem_siga_count} / {resumo.total_demandas}
              </div>
              <div className={`text-xs mt-0.5 ${resumo.sem_siga_count > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {resumo.sem_siga_count > 0
                  ? `⚠️ ${resumo.sem_siga_count} sem número TLB-PRO`
                  : '✅ 100% autuadas no SIGA'}
              </div>
            </div>

            {/* Card 4: Urgências Fabricadas */}
            <div className="bg-slate-900/60 border border-slate-700/60 rounded-xl p-4">
              <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
                <span>Urgências Fabricadas</span>
                <span className="text-xs">🚨</span>
              </div>
              <div className="text-xl font-bold text-white mt-1">
                {resumo.urgencias_fabricadas_count} alertas
              </div>
              <div className={`text-xs mt-0.5 ${resumo.urgencias_fabricadas_count > 0 ? 'text-rose-400' : 'text-slate-400'}`}>
                {resumo.urgencias_fabricadas_count > 0
                  ? 'Inércia da área ou data fatal vencida'
                  : 'Nenhum desvio detectado'}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Barra de Navegação Horizontal das Colunas do Kanban */}
      <div className="bg-slate-850 border border-slate-700/80 rounded-2xl px-5 py-3.5 flex flex-col md:flex-row md:items-center justify-between gap-3 shadow-md">
        <div className="flex items-center gap-3 flex-wrap">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-950 border border-blue-600/50 text-blue-300 font-bold text-xs shadow-sm">
            <span>👁️</span> Exibindo 3 Colunas com Largura Ampla
          </span>
          <span className="text-xs text-slate-300 hidden sm:inline">
            Role para o lado ou clique nos botões para navegar entre <b>1. Levantamento</b>, <b>2. Validação</b>, <b>3. Consolidação</b> e puxar <b>4. Deliberação REDIR</b> e <b>5. Calendário Oficial</b>.
          </span>
        </div>

        {/* Controles de Rolagem Rápida */}
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={() => scrollToFase('inicio')}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-300 hover:text-white border border-slate-600 rounded-xl text-xs font-semibold transition flex items-center gap-1"
            title="Ir para o início: 1. Levantamento, 2. Validação e 3. Consolidação"
          >
            <span>⏮️</span> Início (1 a 3)
          </button>

          <button
            type="button"
            onClick={() => scrollKanban(-1)}
            className="p-1.5 px-2.5 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-200 border border-slate-600 rounded-xl text-xs font-bold transition flex items-center gap-1"
            title="Rolar para a esquerda"
          >
            ◀
          </button>

          <button
            type="button"
            onClick={() => scrollKanban(1)}
            className="p-1.5 px-2.5 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-200 border border-slate-600 rounded-xl text-xs font-bold transition flex items-center gap-1"
            title="Rolar para a direita"
          >
            ▶
          </button>

          <button
            type="button"
            onClick={() => scrollToFase('deliberacao')}
            className="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 active:scale-95 text-white rounded-xl text-xs font-bold transition flex items-center gap-1.5 shadow-md shadow-blue-900/30"
            title="Avançar diretamente para 4. Deliberação REDIR e 5. Calendário Oficial"
          >
            <span>Fases 4 &amp; 5</span> <span>⏭️</span>
          </button>
        </div>
      </div>

      {/* 5 Colunas do Kanban de Governança com Scroll Horizontal */}
      {loading ? (
        <div className="text-center py-20 text-slate-400">
          <div className="inline-block animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500 mb-3"></div>
          <div className="text-sm font-medium">Carregando Esteira de Governança do PLAC...</div>
        </div>
      ) : (
        <div
          ref={kanbanScrollRef}
          className="flex gap-4 overflow-x-auto pb-6 pt-1 items-start scroll-smooth w-full"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: '#3b82f6 #1e293b'
          }}
        >
          {/* FASE 1: Levantamento de Necessidades */}
          <KanbanColuna
            titulo="1. Levantamento"
            subtitulo="Área Demandante"
            cor="border-slate-600 bg-slate-800/40"
            badgeCor="bg-slate-700 text-slate-300"
            icon="📝"
            demandas={colunas.levantamento}
            onOpenCertidao={setSelectedDemandForCertidao}
            onAvancar={handleAvancarFase}
            onDevolver={(d) => setDevolverTarget(d)}
            actionLoading={actionLoading}
            faseAtual="AGUARDANDO_VALIDACAO"
          />

          {/* FASE 2: Validação da Diretoria */}
          <KanbanColuna
            titulo="2. Validação Diretor"
            subtitulo="Julgamento Estratégico"
            cor="border-blue-700/60 bg-blue-950/20"
            badgeCor="bg-blue-600/30 text-blue-300"
            icon="⚖️"
            demandas={colunas.validacao_diretor}
            onOpenCertidao={setSelectedDemandForCertidao}
            onAvancar={handleAvancarFase}
            onDevolver={(d) => setDevolverTarget(d)}
            actionLoading={actionLoading}
            faseAtual="VALIDADO_DIRETOR"
          />

          {/* FASE 3: Consolidação GCC & SLA */}
          <KanbanColuna
            titulo="3. Consolidação GCC"
            subtitulo="Instrução & 10 SLAs"
            cor="border-purple-700/60 bg-purple-950/20"
            badgeCor="bg-purple-600/30 text-purple-300"
            icon="🏢"
            demandas={colunas.consolidacao_gcc}
            onOpenCertidao={setSelectedDemandForCertidao}
            onAvancar={handleAvancarFase}
            onDevolver={(d) => setDevolverTarget(d)}
            actionLoading={actionLoading}
            faseAtual="CONSOLIDADO"
          />

          {/* FASE 4: Deliberação REDIR & DAFRI */}
          <KanbanColuna
            titulo="4. Deliberação REDIR"
            subtitulo="Parecer DAFRI & Colegiado"
            cor="border-amber-700/60 bg-amber-950/20"
            badgeCor="bg-amber-600/30 text-amber-300"
            icon="🏛️"
            demandas={colunas.deliberacao_redir}
            onOpenCertidao={setSelectedDemandForCertidao}
            onAvancar={handleAvancarFase}
            onDevolver={(d) => setDevolverTarget(d)}
            actionLoading={actionLoading}
            faseAtual="DELIBERACAO_REDIR"
          />

          {/* FASE 5: Calendário de Contratações Vigentes */}
          <KanbanColuna
            titulo="5. Calendário Oficial"
            subtitulo="Homologado & Vigente"
            cor="border-emerald-700/60 bg-emerald-950/20"
            badgeCor="bg-emerald-600/30 text-emerald-300"
            icon="✅"
            demandas={colunas.calendario_vigente}
            onOpenCertidao={setSelectedDemandForCertidao}
            onAvancar={handleAvancarFase}
            onDevolver={(d) => setDevolverTarget(d)}
            actionLoading={actionLoading}
            faseAtual="VIGENTE"
          />
        </div>
      )}

      {/* Modal de Certidão e Amarração do SIGA */}
      {selectedDemandForCertidao && (
        <CertidaoVinculacaoModal
          demand={selectedDemandForCertidao}
          onClose={() => setSelectedDemandForCertidao(null)}
          onSuccess={() => {
            setSelectedDemandForCertidao(null);
            fetchKanban();
            showFeedback('Processo SIGA vinculado com sucesso à demanda!');
          }}
        />
      )}

      {/* Modal de Devolução para Ajustes */}
      {devolverTarget && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-850 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-700 pb-3">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <span>↩️</span> Devolver Demanda para Ajustes
              </h3>
              <button onClick={() => setDevolverTarget(null)} className="text-slate-400 hover:text-white">✕</button>
            </div>

            <p className="text-xs text-slate-300">
              A demanda <span className="font-mono font-bold text-blue-400">{devolverTarget.codigo_rastreio_plac || '#' + devolverTarget.id}</span> retornará para a etapa anterior para correção pela Área Demandante.
            </p>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Motivo / Justificativa da Devolução (Obrigatório):
              </label>
              <textarea
                value={motivoDevolucao}
                onChange={(e) => setMotivoDevolucao(e.target.value)}
                placeholder="Descreva detalhadamente o ajuste necessário no ETP, justificativa ou quantitativo..."
                rows={4}
                className="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setDevolverTarget(null)}
                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-xs font-semibold hover:bg-slate-700"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmDevolver}
                disabled={actionLoading}
                className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-bold transition disabled:opacity-50"
              >
                {actionLoading ? 'Processando...' : 'Confirmar Devolução'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Subcomponente de Coluna Kanban com Largura Ampla (Exibe até 3 colunas e scroll para o resto)
function KanbanColuna({
  titulo,
  subtitulo,
  cor,
  badgeCor,
  icon,
  demandas = [],
  onOpenCertidao,
  onAvancar,
  onDevolver,
  actionLoading,
  faseAtual
}) {
  return (
    <div
      className={`border rounded-2xl p-4 shadow-xl flex flex-col min-h-[580px] shrink-0 transition-all ${cor}`}
      style={{
        width: 'calc((100% - 2rem) / 3)',
        minWidth: '380px',
        maxWidth: '520px'
      }}
    >
      {/* Topo da Coluna */}
      <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-700/60">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <div>
            <h3 className="text-sm font-bold text-white leading-tight">{titulo}</h3>
            <p className="text-[11px] text-slate-400">{subtitulo}</p>
          </div>
        </div>
        <span className={`text-xs font-bold px-2.5 py-1 rounded-full shadow-sm ${badgeCor}`}>
          {demandas.length} {demandas.length === 1 ? 'item' : 'itens'}
        </span>
      </div>

      {/* Lista de Cartões */}
      <div className="space-y-3.5 flex-1 overflow-y-auto max-h-[720px] pr-1.5">
        {demandas.length === 0 ? (
          <div className="text-center py-16 text-xs text-slate-500 italic bg-slate-900/30 rounded-xl border border-dashed border-slate-800">
            Nenhuma demanda nesta fase
          </div>
        ) : (
          demandas.map((d) => (
            <KanbanCard
              key={d.id}
              demand={d}
              faseAtual={faseAtual}
              onOpenCertidao={onOpenCertidao}
              onAvancar={onAvancar}
              onDevolver={onDevolver}
              actionLoading={actionLoading}
            />
          ))
        )}
      </div>
    </div>
  );
}

// Subcomponente de Cartão de Demanda com Layout Amplo e Espaçoso
function KanbanCard({
  demand,
  faseAtual,
  onOpenCertidao,
  onAvancar,
  onDevolver,
  actionLoading
}) {
  const formatBRL = (val) => {
    return Number(val || 0).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  };

  const temSiga = Boolean(demand.siga_process_number && demand.siga_process_number.trim());
  const codRastreio = demand.codigo_rastreio_plac || `PLAC-${demand.id}`;

  return (
    <div className="bg-slate-900/95 border border-slate-700 hover:border-blue-500/60 rounded-xl p-4 shadow-md hover:shadow-xl transition-all space-y-3 group">
      {/* Badges de Topo */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span className="font-mono text-xs font-bold bg-blue-950/90 text-blue-300 border border-blue-700/60 px-2 py-0.5 rounded shadow-sm">
          🏷️ {codRastreio}
        </span>
        <div className="flex items-center gap-1.5">
          <span className="text-[11px] font-bold px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700 shadow-sm">
            {demand.quadrimestre_alvo || 'Q-N/D'}
          </span>
          <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700">
            {demand.year || 2026}
          </span>
        </div>
      </div>

      {/* Objeto e Informações com Espaçamento Amplo */}
      <div>
        <h4 className="text-sm font-medium text-slate-100 line-clamp-3 leading-snug group-hover:text-white transition">
          {demand.description}
        </h4>
        <div className="text-xs text-slate-400 mt-2 flex items-center justify-between pt-1 border-t border-slate-800/60">
          <span className="font-medium text-slate-300">{demand.directorate || 'Diretoria'}</span>
          <span className="text-emerald-400 font-bold text-sm">{formatBRL(demand.estimated_value)}</span>
        </div>
      </div>

      {/* Status da Amarração SIGA */}
      <div className="text-xs">
        {temSiga ? (
          <div className="flex items-center justify-between bg-emerald-950/50 border border-emerald-800/50 rounded-lg px-2.5 py-1.5 text-emerald-300 shadow-sm">
            <span className="font-mono font-bold text-[11px]">📁 {demand.siga_process_number}</span>
            <span className="text-[10px] text-emerald-300 bg-emerald-900/60 border border-emerald-700 px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">
              Autuado
            </span>
          </div>
        ) : (
          <div className="bg-rose-950/50 border border-rose-800/50 rounded-lg px-2.5 py-1.5 text-rose-300 flex items-center justify-between shadow-sm">
            <span className="font-medium text-[11px]">⚠️ Processo SIGA Não Autuado</span>
            <span className="text-[10px] text-rose-300 bg-rose-900/60 border border-rose-700 px-1.5 py-0.5 rounded font-bold uppercase tracking-wider">
              Pendente
            </span>
          </div>
        )}
      </div>

      {/* Modalidade e SLA (se já consolidados) */}
      {demand.procurement_type && (
        <div className="text-xs bg-slate-800/90 rounded-lg p-2 text-slate-300 flex items-center justify-between border border-slate-700/60">
          <span className="text-[11px]">Modalidade: <b className="text-slate-100">{demand.procurement_type}</b></span>
          {demand.sla_days && (
            <span className="text-blue-400 font-bold text-[11px] bg-blue-950/80 px-2 py-0.5 rounded border border-blue-800/60">
              {demand.sla_days} dias úteis
            </span>
          )}
        </div>
      )}

      {/* Alerta de Urgência Fabricada / Inércia */}
      {demand.needs_anticipation && (
        <div className="text-xs bg-amber-950/60 border border-amber-800/60 rounded-lg p-2 text-amber-300 flex items-center gap-1.5">
          <span>⚠️</span>
          <span className="text-[11px] font-medium leading-tight">Alerta de Inércia: Exige antecipação de prazo</span>
        </div>
      )}

      {/* Barra de Ações do Cartão */}
      <div className="pt-2 flex items-center justify-between gap-2 border-t border-slate-800">
        {/* Botão de Certidão & SIGA */}
        <button
          onClick={() => onOpenCertidao(demand)}
          className="flex-1 bg-slate-800 hover:bg-slate-700 active:scale-95 text-slate-200 border border-slate-700 hover:border-slate-500 text-xs font-semibold py-1.5 px-2.5 rounded-lg transition text-center flex items-center justify-center gap-1 shadow-sm"
          title="Ver Certidão Oficial em PDF e Vincular Processo SIGA"
        >
          <span>📄</span>
          <span>Certidão &amp; SIGA</span>
        </button>

        {/* Botão de Transição de Fase */}
        {faseAtual !== 'VIGENTE' && (
          <button
            onClick={() => onAvancar(demand)}
            disabled={actionLoading}
            className={`flex-1 text-xs font-bold py-1.5 px-2.5 rounded-lg transition text-center shadow-md active:scale-95 flex items-center justify-center gap-1 ${
              !temSiga && faseAtual === 'AGUARDANDO_VALIDACAO'
                ? 'bg-rose-900/60 hover:bg-rose-800 border border-rose-700/60 text-rose-200 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 text-white'
            }`}
            title={!temSiga && faseAtual === 'AGUARDANDO_VALIDACAO' ? 'Bloqueado: Requer processo SIGA autuado' : 'Avançar para a próxima fase'}
          >
            {!temSiga && faseAtual === 'AGUARDANDO_VALIDACAO' ? (
              <><span>🔒</span><span>Bloqueado</span></>
            ) : (
              <><span>Avançar</span><span>➔</span></>
            )}
          </button>
        )}

        {/* Botão de Devolver se não estiver na fase 1 */}
        {faseAtual !== 'AGUARDANDO_VALIDACAO' && faseAtual !== 'VIGENTE' && (
          <button
            onClick={() => onDevolver(demand)}
            className="bg-slate-800 hover:bg-amber-900/50 hover:text-amber-200 text-slate-400 border border-slate-700 text-xs font-bold py-1.5 px-2.5 rounded-lg transition active:scale-95 shadow-sm"
            title="Devolver demanda para ajustes da Área Demandante"
          >
            ↩️
          </button>
        )}
      </div>
    </div>
  );
}
