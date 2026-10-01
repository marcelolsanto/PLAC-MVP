/**
 * GovernancaEsteiraKanban.jsx
 * Esteira de Governança do PLAC 2026 — Funil completo (6 colunas)
 * Coluna "1. Levantamento" exibe cards enriquecidos com telemetria SIGA:
 *  • COD_VERIF vinculado à planilha PLAC
 *  • Custodiante atual (quem está com o processo)
 *  • Setor atual no SIGA (onde está parado)
 *  • Motivo do represamento (diagnóstico automático)
 *  • Checklist de pendências para Validação do Diretor
 *  • Documentos juntados ao processo SIGA
 */

import { useState, useEffect } from "react";

const API = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";
const fetchJSON = (url) =>
  fetch(url, { headers: { Accept: "application/json" } }).then((r) => r.json());

// ─── Helpers ─────────────────────────────────────────────────────────────────
const fmtBRL = (v) =>
  v != null
    ? new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 0 }).format(v)
    : "N/D";

const fmtDate = (s) => {
  if (!s) return "—";
  const d = new Date(s.replace(" ", "T"));
  return isNaN(d) ? s : d.toLocaleDateString("pt-BR");
};

// ─── Badge ────────────────────────────────────────────────────────────────────
const Badge = ({ label, color = "slate" }) => {
  const map = {
    blue:    "bg-blue-700/70 text-blue-200 border-blue-600/50",
    emerald: "bg-emerald-700/70 text-emerald-200 border-emerald-600/50",
    amber:   "bg-amber-700/70 text-amber-200 border-amber-600/50",
    red:     "bg-red-700/70 text-red-200 border-red-600/50",
    slate:   "bg-slate-700/70 text-slate-300 border-slate-600/50",
    violet:  "bg-violet-800/70 text-violet-200 border-violet-700/50",
    cyan:    "bg-cyan-800/70 text-cyan-200 border-cyan-700/50",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold border ${map[color] ?? map.slate}`}>
      {label}
    </span>
  );
};

const PrazoChip = ({ status, desvio }) => {
  if (status === "CRITICO")  return <span className="flex items-center gap-1 text-[10px] font-bold text-red-300 bg-red-900/40 border border-red-700/60 rounded px-2 py-0.5">🔴 CRÍTICO {desvio}</span>;
  if (status === "ATENCAO")  return <span className="flex items-center gap-1 text-[10px] font-bold text-amber-300 bg-amber-900/40 border border-amber-700/60 rounded px-2 py-0.5">🟡 ATENÇÃO {desvio}</span>;
  return <span className="flex items-center gap-1 text-[10px] font-bold text-emerald-300 bg-emerald-900/40 border border-emerald-700/60 rounded px-2 py-0.5">🟢 NO PRAZO {desvio}</span>;
};

// ─── Pendência Item ───────────────────────────────────────────────────────────
const PendenciaItem = ({ pend }) => {
  const [expanded, setExpanded] = useState(false);
  const urgColors = {
    CRITICA: "text-red-400 border-red-700/50 bg-red-900/20",
    ALTA:    "text-amber-400 border-amber-700/50 bg-amber-900/20",
    MEDIA:   "text-yellow-400 border-yellow-700/50 bg-yellow-900/20",
    OK:      "text-emerald-400 border-emerald-700/50 bg-emerald-900/20",
  };
  const icon = pend.concluido ? "✅" : pend.urgencia === "CRITICA" ? "🚨" : pend.urgencia === "ALTA" ? "⚠️" : "📋";
  return (
    <div
      className={`border rounded-md p-2 cursor-pointer transition-all ${
        pend.concluido ? "border-emerald-700/30 bg-emerald-900/10 opacity-60" : (urgColors[pend.urgencia] ?? "border-slate-600/30 bg-slate-800/30")
      }`}
      onClick={() => setExpanded((e) => !e)}
    >
      <div className="flex items-start gap-2">
        <span className="text-sm flex-shrink-0 mt-0.5">{icon}</span>
        <div className="flex-1 min-w-0">
          <p className={`text-[11px] font-medium leading-tight ${pend.concluido ? "line-through text-slate-400" : "text-slate-200"}`}>{pend.descricao}</p>
          {expanded && !pend.concluido && (
            <p className="text-[10px] text-slate-400 mt-1 leading-tight">💡 {pend.instrucao}</p>
          )}
        </div>
        {!pend.concluido && <span className="text-[9px] text-slate-500 ml-1">{expanded ? "▲" : "▼"}</span>}
      </div>
    </div>
  );
};

// ─── Documento Item ───────────────────────────────────────────────────────────
const DocItem = ({ doc }) => {
  const ext = (doc.titulo || "").split(".").pop().toUpperCase();
  const extColors = { PDF: "text-red-400 bg-red-900/30", DOCX: "text-blue-400 bg-blue-900/30", XLSX: "text-emerald-400 bg-emerald-900/30" };
  return (
    <div className="flex items-start gap-2 py-1.5 border-b border-slate-700/30 last:border-0">
      <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded flex-shrink-0 mt-0.5 ${extColors[ext] ?? "text-slate-400 bg-slate-700/30"}`}>{ext}</span>
      <div className="flex-1 min-w-0">
        <p className="text-[11px] text-slate-200 truncate font-medium">{doc.titulo}</p>
        <div className="flex gap-2 flex-wrap mt-0.5">
          <span className="text-[9px] text-slate-400">📅 {fmtDate(doc.data_juntada)}</span>
          {doc.signatario && <span className="text-[9px] text-slate-400">✍️ {doc.signatario}</span>}
          {doc.tamanho_kb && <span className="text-[9px] text-slate-500">{doc.tamanho_kb} KB</span>}
        </div>
        {doc.resumo_conteudo && <p className="text-[9px] text-slate-500 mt-0.5 leading-tight line-clamp-2">{doc.resumo_conteudo}</p>}
      </div>
    </div>
  );
};

// ─── Card Levantamento Enriquecido ────────────────────────────────────────────
const LevantamentoCard = ({ demand, onAvancar }) => {
  const tel = demand.siga_telemetria ?? {};
  const pendencias = tel.pendencias_validacao_diretor ?? [];
  const documentos = tel.documentos_juntados ?? [];
  const totalPend = tel.total_pendencias ?? 0;
  const concluidas = pendencias.filter((p) => p.concluido).length;
  const progressPct = pendencias.length > 0 ? Math.round((concluidas / pendencias.length) * 100) : 0;

  const [showDocs, setShowDocs] = useState(false);
  const [showPend, setShowPend] = useState(true);
  const temSiga = tel.tem_siga ?? false;

  return (
    <div className="bg-slate-800/90 border border-slate-600/60 rounded-xl shadow-lg flex flex-col w-full flex-shrink-0 overflow-hidden hover:border-slate-500/80 transition-all duration-200">

      {/* ── Cabeçalho ── */}
      <div className="bg-gradient-to-r from-slate-700/60 to-slate-800/40 px-4 py-3 border-b border-slate-700/50">
        <div className="flex items-start justify-between gap-2">
          <div className="flex flex-wrap gap-1.5 items-center">
            <Badge label={`PLAC-${demand.id}`} color="violet" />
            <Badge label={`Q-${demand.quadrimestre_alvo ?? "N/D"}`} color="violet" />
            {tel.cod_verif && (
              <span
                title={`COD_VERIF planilha PLAC 2026 — aba BASE_PLAC_2026\nLinha: ${tel.cod_verif}`}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold border border-cyan-600/50 bg-cyan-900/40 text-cyan-200 cursor-help"
              >
                📋 {tel.cod_verif}
              </span>
            )}
            {temSiga
              ? <Badge label="✅ SIGA Autuado" color="emerald" />
              : <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold border border-red-600/60 bg-red-900/40 text-red-300 animate-pulse">⚠️ SIGA Não Autuado</span>
            }
          </div>
          {tel.status_prazo && <PrazoChip status={tel.status_prazo} desvio={tel.desvio_str ?? ""} />}
        </div>

        <p className="text-[12px] font-semibold text-white mt-2 leading-snug line-clamp-3" title={demand.description}>
          {demand.description}
        </p>

        <div className="flex flex-wrap gap-2 mt-2 items-center">
          <span className="text-[10px] text-slate-300">🏛️ {demand.directorate || "—"}</span>
          <span className="text-[13px] font-bold text-emerald-400">{fmtBRL(demand.estimated_value)}</span>
        </div>
        <div className="flex flex-wrap gap-1.5 mt-1.5">
          {demand.procurement_type && <Badge label={demand.procurement_type} color="blue" />}
          {tel.sla_modalidade && <Badge label={`SLA: ${tel.sla_modalidade} d.u.`} color="slate" />}
          {demand.needs_anticipation && <Badge label="🚀 ANTECIPAÇÃO" color="amber" />}
        </div>
      </div>

      {/* ── Localização SIGA ── */}
      <div className="px-4 py-3 border-b border-slate-700/40 bg-slate-800/50">
        <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mb-2">📍 Localização no SIGA</p>

        <div className="flex items-start gap-2 mb-2">
          <span className="text-[10px] text-slate-500 w-16 flex-shrink-0 pt-0.5">Setor</span>
          <div>
            <span className="text-[11px] font-bold text-amber-300 bg-amber-900/30 border border-amber-700/40 rounded px-2 py-0.5">{tel.setor_atual_sigla ?? "—"}</span>
            {tel.setor_atual_nome && <p className="text-[10px] text-slate-400 mt-0.5 leading-tight">{tel.setor_atual_nome}</p>}
          </div>
        </div>

        <div className="flex items-start gap-2 mb-2">
          <span className="text-[10px] text-slate-500 w-16 flex-shrink-0 pt-0.5">Com quem</span>
          <div className="flex items-center gap-1.5">
            <span className="w-5 h-5 rounded-full bg-slate-600 border border-slate-500 flex items-center justify-center text-[9px] flex-shrink-0">👤</span>
            <p className="text-[11px] text-slate-200 font-medium leading-tight">{tel.custodiante_atual ?? "—"}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] text-slate-500 w-16 flex-shrink-0">Parado há</span>
          <span className={`text-[12px] font-bold ${(tel.dias_no_setor ?? 0) > 20 ? "text-red-400" : (tel.dias_no_setor ?? 0) > 10 ? "text-amber-400" : "text-emerald-400"}`}>
            {tel.dias_no_setor ?? 0} d.u.
          </span>
          <span className="text-[10px] text-slate-500">(média: 15 d.u.)</span>
        </div>

        <div className="mt-2">
          <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${(tel.dias_no_setor ?? 0) > 20 ? "bg-red-500" : (tel.dias_no_setor ?? 0) > 10 ? "bg-amber-500" : "bg-emerald-500"}`}
              style={{ width: `${Math.min(100, ((tel.dias_no_setor ?? 0) / 30) * 100)}%` }}
            />
          </div>
          <p className="text-[9px] text-slate-500 mt-0.5 text-right">{Math.min(100, Math.round(((tel.dias_no_setor ?? 0) / 30) * 100))}% do limite (~30 d.u.)</p>
        </div>
      </div>

      {/* ── Por que está parado ── */}
      {tel.motivo_parado && (
        <div className="px-4 py-3 border-b border-slate-700/40 bg-amber-950/20">
          <p className="text-[9px] font-bold text-amber-400 uppercase tracking-widest mb-1.5">🔍 Por que está parado</p>
          <p className="text-[11px] text-slate-300 leading-relaxed">{tel.motivo_parado}</p>
          {tel.ultimo_despacho_siga && (
            <p className="text-[10px] text-slate-500 mt-1.5 italic">Último despacho: {tel.ultimo_despacho_siga}</p>
          )}
        </div>
      )}

      {/* ── Checklist pendências ── */}
      {pendencias.length > 0 && (
        <div className="px-4 py-3 border-b border-slate-700/40">
          <button onClick={() => setShowPend((s) => !s)} className="w-full flex items-center justify-between mb-2 group">
            <div className="flex items-center gap-2">
              <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">📌 O que falta para o Diretor</p>
              {totalPend > 0 && <span className="text-[9px] font-bold text-red-300 bg-red-900/40 border border-red-700/50 rounded-full px-1.5">{totalPend} pend.</span>}
            </div>
            <span className="text-[9px] text-slate-500 group-hover:text-slate-300">{showPend ? "▲" : "▼"}</span>
          </button>

          <div className="flex items-center gap-2 mb-2">
            <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${progressPct}%` }} />
            </div>
            <span className="text-[9px] text-slate-400 font-bold w-16 text-right">{concluidas}/{pendencias.length} feitos</span>
          </div>

          {showPend && (
            <div className="flex flex-col gap-1.5">
              {pendencias.map((pend) => <PendenciaItem key={pend.id} pend={pend} />)}
            </div>
          )}
        </div>
      )}

      {/* ── Documentos ── */}
      <div className="px-4 py-3 border-b border-slate-700/40">
        <button onClick={() => setShowDocs((s) => !s)} className="w-full flex items-center justify-between group">
          <div className="flex items-center gap-2">
            <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">📄 Peças do Processo</p>
            <span className="text-[9px] font-bold text-slate-300 bg-slate-700/60 border border-slate-600/50 rounded-full px-1.5">{documentos.length}</span>
          </div>
          <span className="text-[9px] text-slate-500 group-hover:text-slate-300">{showDocs ? "▲" : "▼ ver peças"}</span>
        </button>

        {showDocs && documentos.length > 0 && (
          <div className="mt-2 flex flex-col">
            {documentos.map((doc, i) => <DocItem key={doc.id ?? i} doc={doc} />)}
          </div>
        )}
        {showDocs && documentos.length === 0 && (
          <p className="text-[11px] text-slate-500 mt-2 italic">Nenhum documento juntado ao processo SIGA.</p>
        )}
      </div>

      {/* ── Ações ── */}
      <div className="px-4 py-3 flex gap-2">
        <button
          className="flex-1 flex items-center justify-center gap-1.5 text-[11px] font-semibold py-2 rounded-lg border border-blue-600/60 bg-blue-700/30 text-blue-300 hover:bg-blue-700/50 transition-colors"
          onClick={() => window.open(`${API}/demands/${demand.id}/gerar_certidao/`, "_blank")}
        >
          📄 Certidão & SIGA
        </button>
        {temSiga && totalPend === 0 ? (
          <button
            className="flex-1 flex items-center justify-center gap-1.5 text-[11px] font-semibold py-2 rounded-lg border border-emerald-600/60 bg-emerald-700/40 text-emerald-300 hover:bg-emerald-700/60 transition-colors"
            onClick={() => onAvancar && onAvancar(demand.id)}
          >
            ✅ Enviar ao Diretor
          </button>
        ) : (
          <button
            className="flex-1 flex items-center justify-center gap-1.5 text-[11px] font-semibold py-2 rounded-lg border border-slate-600/40 bg-slate-700/30 text-slate-500 cursor-not-allowed"
            disabled
            title={`${totalPend} pendência(s) impedem o avanço`}
          >
            🔒 Bloqueado ({totalPend} pend.)
          </button>
        )}
      </div>

      {demand.siga_process_number && (
        <div className="px-4 pb-2.5">
          <p className="text-[10px] text-slate-500 font-mono">SIGA: {demand.siga_process_number}</p>
        </div>
      )}
    </div>
  );
};

// ─── Card Simples (outras colunas) ────────────────────────────────────────────
const SimpleCard = ({ demand }) => (
  <div className="bg-slate-800/80 border border-slate-700/60 rounded-lg p-3 hover:border-slate-600 transition-colors">
    <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
      <Badge label={`PLAC-${demand.id}`} color="slate" />
      <Badge label={`Q-${demand.quadrimestre_alvo ?? "N/D"}`} color="violet" />
    </div>
    <p className="text-[11px] font-medium text-slate-200 leading-snug line-clamp-2 mb-1.5">{demand.description}</p>
    <div className="flex justify-between items-center">
      <span className="text-[10px] text-slate-400">{demand.procurement_type ?? "—"}</span>
      <span className="text-[11px] font-bold text-emerald-400">{fmtBRL(demand.estimated_value)}</span>
    </div>
  </div>
);

// ─── Coluna ───────────────────────────────────────────────────────────────────
const KanbanColuna = ({ titulo, emoji, cor, cards, renderCard }) => {
  const colorMap = {
    blue:    "from-blue-900/40 to-slate-900/20 border-blue-700/40",
    violet:  "from-violet-900/40 to-slate-900/20 border-violet-700/40",
    emerald: "from-emerald-900/40 to-slate-900/20 border-emerald-700/40",
    amber:   "from-amber-900/40 to-slate-900/20 border-amber-700/40",
    cyan:    "from-cyan-900/40 to-slate-900/20 border-cyan-700/40",
    red:     "from-red-900/40 to-slate-900/20 border-red-700/40",
  };
  const headerMap = {
    blue:    "text-blue-300 border-blue-700/50",
    violet:  "text-violet-300 border-violet-700/50",
    emerald: "text-emerald-300 border-emerald-700/50",
    amber:   "text-amber-300 border-amber-700/50",
    cyan:    "text-cyan-300 border-cyan-700/50",
    red:     "text-red-300 border-red-700/50",
  };
  return (
    <div 
      className={`flex flex-col rounded-xl border bg-gradient-to-b ${colorMap[cor]} flex-shrink-0`}
      style={{ minWidth: '420px', width: '420px' }}
    >
      <div className={`px-4 py-3 border-b ${headerMap[cor]} flex items-center justify-between`}>
        <span className="text-[14px] font-bold tracking-tight">{emoji} {titulo}</span>
        <span className="text-[12px] font-bold bg-slate-800/60 border border-slate-700/60 text-slate-300 rounded-full px-2.5 py-0.5 flex items-center justify-center">{cards.length}</span>
      </div>
      <div className="flex-1 p-3 overflow-y-auto overflow-x-hidden flex flex-col gap-4 max-h-[72vh]">
        {cards.length === 0
          ? <p className="text-[12px] text-slate-600 italic text-center py-6 w-full">Nenhuma demanda nesta fase</p>
          : cards.map((d) => <div key={d.id} className="w-full">{renderCard(d)}</div>)
        }
      </div>
    </div>
  );
};

// ─── KPI Bar ─────────────────────────────────────────────────────────────────
const KpiBar = ({ resumo }) => {
  if (!resumo) return null;
  const fases = resumo.fases ?? {};
  const items = [
    { label: "Levantamento",      val: fases.levantamento ?? 0,        color: "text-blue-400" },
    { label: "Validação Dir.",     val: fases.validacao_diretor ?? 0,   color: "text-violet-400" },
    { label: "Consolidação GCC",  val: fases.consolidacao_gcc ?? 0,    color: "text-emerald-400" },
    { label: "Delib. REDIR",      val: fases.deliberacao_redir ?? 0,   color: "text-amber-400" },
    { label: "Vigente",           val: fases.calendario_vigente ?? 0,  color: "text-cyan-400" },
    { label: "Devolvido",         val: fases.devolvido_ajustes ?? 0,   color: "text-red-400" },
    { label: "Sem SIGA ⚠️",       val: resumo.sem_siga_count ?? 0,     color: "text-red-300" },
  ];
  return (
    <div className="flex flex-wrap gap-3 px-4 py-3 bg-slate-900/60 border-b border-slate-700/50">
      {items.map(({ label, val, color }) => (
        <div key={label} className="flex flex-col items-center min-w-[70px]">
          <span className={`text-[18px] font-bold ${color}`}>{val}</span>
          <span className="text-[9px] text-slate-500 text-center leading-tight">{label}</span>
        </div>
      ))}
      {resumo.orcamento_total != null && (
        <div className="flex flex-col items-center min-w-[110px] border-l border-slate-700 pl-3 ml-1">
          <span className="text-[15px] font-bold text-emerald-300">{fmtBRL(resumo.orcamento_total)}</span>
          <span className="text-[9px] text-slate-500">Orçamento Total PLAC</span>
        </div>
      )}
    </div>
  );
};

// ─── Main ─────────────────────────────────────────────────────────────────────
export default function GovernancaEsteiraKanban() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtroQ, setFiltroQ] = useState("");
  const [avancandoId, setAvancandoId] = useState(null);

  const carregar = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = filtroQ ? `?quadrimestre=${filtroQ}&ano=2026` : "?ano=2026";
      const json = await fetchJSON(`${API}/demands/esteira_kanban/${params}`);
      setData(json);
    } catch (e) {
      setError("Erro ao carregar esteira: " + e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { carregar(); }, [filtroQ]);

  const handleAvancar = async (demandId) => {
    if (avancandoId) return;
    setAvancandoId(demandId);
    try {
      const res = await fetch(`${API}/demands/${demandId}/avancar_fase/`, { method: "POST", headers: { "Content-Type": "application/json" } });
      const json = await res.json();
      if (!res.ok) alert(json.error || "Erro ao avançar fase.");
      else await carregar();
    } catch (e) {
      alert("Erro de rede: " + e.message);
    } finally {
      setAvancandoId(null);
    }
  };

  const colunas = data?.colunas ?? {};
  const resumo = data?.resumo;

  const colunasDef = [
    { key: "levantamento",       titulo: "1. Levantamento",       emoji: "📥", cor: "blue",    isFirst: true, renderCard: (d) => <LevantamentoCard demand={d} onAvancar={handleAvancar} /> },
    { key: "validacao_diretor",  titulo: "2. Validação Diretor",  emoji: "✅", cor: "violet",   renderCard: (d) => <SimpleCard demand={d} /> },
    { key: "consolidacao_gcc",   titulo: "3. Consolidação GCC",   emoji: "⚙️", cor: "emerald",  renderCard: (d) => <SimpleCard demand={d} /> },
    { key: "deliberacao_redir",  titulo: "4. Deliberação REDIR",  emoji: "🏛️", cor: "amber",    renderCard: (d) => <SimpleCard demand={d} /> },
    { key: "calendario_vigente", titulo: "5. Calendário Vigente", emoji: "📆", cor: "cyan",     renderCard: (d) => <SimpleCard demand={d} /> },
    { key: "devolvido_ajustes",  titulo: "↩️ Devolvidos",         emoji: "🔄", cor: "red",      renderCard: (d) => <SimpleCard demand={d} /> },
  ];

  return (
    <div className="flex flex-col h-full bg-slate-900 rounded-xl overflow-hidden border border-slate-700/60">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 bg-slate-800/80 border-b border-slate-700/60">
        <div>
          <h2 className="text-[14px] font-bold text-white">📋 Esteira de Governança — PLAC 2026</h2>
          <p className="text-[10px] text-slate-400 mt-0.5">Funil completo com telemetria SIGA em tempo real • Cards de Levantamento com scroll horizontal</p>
        </div>
        <div className="flex items-center gap-2">
          {["", "Q1", "Q2", "Q3"].map((q) => (
            <button
              key={q}
              onClick={() => setFiltroQ(q)}
              className={`text-[11px] font-semibold px-3 py-1.5 rounded-lg border transition-colors ${
                filtroQ === q ? "bg-blue-600 border-blue-500 text-white" : "bg-slate-700/50 border-slate-600/50 text-slate-300 hover:bg-slate-700"
              }`}
            >
              {q || "Todos"}
            </button>
          ))}
          <button onClick={carregar} disabled={loading} className="text-[11px] font-semibold px-3 py-1.5 rounded-lg border border-slate-600/50 bg-slate-700/50 text-slate-300 hover:bg-slate-700 transition-colors disabled:opacity-50">
            {loading ? "⟳" : "🔄"}
          </button>
        </div>
      </div>

      <KpiBar resumo={resumo} />

      {loading && (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin text-4xl mb-3">⟳</div>
            <p className="text-slate-400 text-sm">Carregando esteira de governança...</p>
          </div>
        </div>
      )}

      {error && (
        <div className="flex-1 flex items-center justify-center px-4">
          <div className="bg-red-900/30 border border-red-700/60 rounded-xl p-6 text-center max-w-lg">
            <p className="text-red-300 font-medium mb-2">⚠️ {error}</p>
            <button onClick={carregar} className="text-sm text-red-400 underline hover:text-red-300">Tentar novamente</button>
          </div>
        </div>
      )}

      {!loading && !error && (
        <div className="flex-1 overflow-x-auto">
          <div className="flex gap-4 p-4 min-w-max h-full">
            {colunasDef.map((col) => (
              <KanbanColuna
                key={col.key}
                titulo={col.titulo}
                emoji={col.emoji}
                cor={col.cor}
                cards={colunas[col.key] ?? []}
                renderCard={col.renderCard}
                isFirst={!!col.isFirst}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
