import React, { useState } from 'react';

import SigaDocumentsModal from './SigaDocumentsModal';
import CertidaoVinculacaoModal from './CertidaoVinculacaoModal';

export default function DemandList({ demands, onNewDemandClick, onEditDemandClick }) {
  
  const [sigaModalProcesso, setSigaModalProcesso] = useState(null);
  const [certidaoModalDemandId, setCertidaoModalDemandId] = useState(null);
  const getPriorityBadge = (level, score) => {
    switch (level) {
      case 'ALTO':
        return (
          <span className="bg-red-500/20 text-red-400 border border-red-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">
            Prioridade Alta ({score} pts)
          </span>
        );
      case 'MEDIO':
        return (
          <span className="bg-amber-500/20 text-amber-400 border border-amber-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">
            Prioridade Média ({score} pts)
          </span>
        );
      case 'BAIXO':
      default:
        return (
          <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-xs px-2.5 py-0.5 rounded-full font-semibold">
            Prioridade Baixa ({score} pts)
          </span>
        );
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'AGUARDANDO_VALIDACAO':
        return (
          <span className="bg-blue-500/10 text-blue-400 border border-blue-500/30 text-xs px-2 py-0.5 rounded">
            Aguardando validação superior
          </span>
        );
      case 'VALIDADO_DIRETOR':
        return (
          <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs px-2 py-0.5 rounded font-medium">
            ✓ Validado pela Diretoria (Fila GCC)
          </span>
        );
      case 'DEVOLVIDO_AJUSTES':
        return (
          <span className="bg-red-500/10 text-red-400 border border-red-500/30 text-xs px-2 py-0.5 rounded font-medium">
            Devolvido para Ajustes
          </span>
        );
      default:
        return <span className="text-slate-400 text-xs">{status}</span>;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-white">Necessidades Registradas</h3>
          <p className="text-xs text-slate-400">Esteira operacional das demandas de contratação</p>
        </div>
        <button
          onClick={onNewDemandClick}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg shadow transition"
        >
          + Nova Necessidade
        </button>
      </div>

      {demands.length === 0 ? (
        <div className="p-8 text-center bg-slate-800 border border-slate-700 rounded-xl text-slate-400">
          Nenhuma demanda registrada até o momento. Clique em "+ Nova Necessidade" para criar a primeira.
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3">
          {demands.map((demand) => (
            <div
              key={demand.id}
              className={`p-4 bg-slate-800 border ${
                demand.status === 'DEVOLVIDO_AJUSTES' ? 'border-red-500/50' : 'border-slate-700'
              } rounded-xl hover:border-slate-600 transition shadow-sm space-y-3`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono bg-slate-900 text-slate-300 px-2 py-0.5 rounded">
                      #{demand.id}
                    </span>
                    <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">
                      {demand.item_type}
                    </span>
                    {getPriorityBadge(demand.priority_level, demand.priority_score)}
                  </div>
                  <h4 className="text-white font-medium text-base pt-1">{demand.description}</h4>
                  <p className="text-xs text-slate-400">
                    Catálogo: <strong className="text-slate-300">{demand.catmat_code}</strong> | Vinculação:{' '}
                    {demand.strategic_alignment}
                  </p>
                </div>

                <div className="text-right space-y-1">
                  <p className="text-white font-semibold text-sm">
                    R$ {Number(demand.estimated_value).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </p>
                  <p className="text-xs text-slate-400">
                    Pretensão: {new Date(demand.intended_date).toLocaleDateString('pt-BR')}
                  </p>
                                    <div className="pt-1 flex items-center gap-2">
                    {getStatusBadge(demand.status)}
                    
                  </div>
                </div>
              </div>

              {/* Barra de Origem e Rastreabilidade Oficial (SIGA / PNCP / PLAC 2027) */}
              <div className="pt-2 border-t border-slate-700/60 flex flex-wrap items-center justify-between gap-2 text-xs">
                <div className="flex flex-wrap items-center gap-1.5">
                  {/* Badge da Fonte de Dados */}
                  {demand.fonte_tipo === 'SIGA_PNCP' ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 font-bold text-[11px]">
                      <span>🏛️ SIGA</span>
                      <span className="text-slate-500">•</span>
                      <span>🌐 PNCP</span>
                    </span>
                  ) : demand.fonte_tipo === 'SIGA' ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-purple-500/20 text-purple-300 border border-purple-500/40 font-bold text-[11px]">
                      <span>🏛️ Fonte: SIGA (Telebras)</span>
                    </span>
                  ) : demand.fonte_tipo === 'PLAC_2027' ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold text-[11px]">
                      <span>📋 Fonte: Planilha PLAC 2027</span>
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-slate-700 text-slate-300 font-bold text-[11px]">
                      <span>📋 Demanda PLAC</span>
                    </span>
                  )}

                  {/* Número do Processo SIGA */}
                  {demand.numero_processo_siga && (
                    <button
                      type="button"
                      onClick={() => setSigaModalProcesso(demand)}
                      className="bg-slate-900 hover:bg-blue-950 border border-blue-900/50 hover:border-blue-500/50 px-2 py-0.5 rounded font-mono text-[11px] text-blue-300 hover:text-blue-200 font-semibold transition cursor-pointer flex items-center gap-1"
                      title="Clique para abrir os autos e volumes do processo no SIGA"
                    >
                      <span>Proc: {demand.numero_processo_siga}</span>
                      <span className="text-[9px]">🔍</span>
                    </button>
                  )}

                  {/* Volume SIGA */}
                  {demand.volume_siga && (
                    <button
                      type="button"
                      onClick={() => setSigaModalProcesso(demand)}
                      className="bg-slate-900/90 hover:bg-amber-950 border border-amber-900/40 hover:border-amber-500/50 px-2 py-0.5 rounded text-[11px] text-amber-300 hover:text-amber-200 font-mono transition cursor-pointer flex items-center gap-1"
                      title="Clique para inspecionar os volumes e peças processuais"
                    >
                      <span>📑 {demand.volume_siga}</span>
                    </button>
                  )}

                  {/* Número do Contrato / Edital */}
                  {demand.numero_contrato && (
                    <button
                      type="button"
                      onClick={() => setSigaModalProcesso(demand)}
                      className="bg-slate-900/90 hover:bg-emerald-950 border border-emerald-900/40 hover:border-emerald-500/50 px-2 py-0.5 rounded text-[11px] text-emerald-300 hover:text-emerald-200 font-mono font-semibold transition cursor-pointer"
                      title="Clique para ver detalhes contratuais e do edital"
                    >
                      📄 {demand.numero_contrato}
                    </button>
                  )}

                  {/* Código de Rastreio PLAC */}
                  {demand.codigo_rastreio_plac && (
                    <span className="bg-blue-950/80 border border-blue-500/50 px-2 py-0.5 rounded font-mono text-[11px] text-blue-300 font-bold flex items-center gap-1">
                      <span>🏷️</span>
                      <span>{demand.codigo_rastreio_plac}</span>
                    </span>
                  )}

                  {/* Botão Certidão Oficial PLAC & Amarração SIGA */}
                  <button
                    type="button"
                    onClick={() => setCertidaoModalDemandId(demand.id)}
                    className="bg-blue-600/20 hover:bg-blue-600/40 border border-blue-500/40 px-2.5 py-0.5 rounded text-[11px] text-blue-300 hover:text-white font-bold transition flex items-center gap-1 cursor-pointer shadow-sm"
                    title="Emitir Certidão Oficial do PLAC (PDF) e Vincular Processo SIGA"
                  >
                    <span>📄 Certidão &amp; SIGA</span>
                  </button>

                  {/* Botão Dossiê SIGA */}
                  <button
                    type="button"
                    onClick={() => setSigaModalProcesso(demand)}
                    className="bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-500/40 px-2.5 py-0.5 rounded text-[11px] text-indigo-300 hover:text-white font-bold transition flex items-center gap-1 cursor-pointer"
                    title="Abrir Dossiê Completo de Autos Eletrônicos no SIGA"
                  >
                    <span>📑 Dossiê SIGA</span>
                  </button>
                </div>

                {/* Links Diretos: SIGA Intranet e PNCP */}
                <div className="flex items-center gap-1.5">
                  {demand.link_siga && (
                    <a
                      href={demand.link_siga}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 hover:text-white border border-indigo-500/30 font-semibold text-[11px] transition shadow-sm"
                      title="Abrir diretamente na Intranet SIGA da Telebras"
                    >
                      <span>🏛️ SIGA Intranet</span>
                      <span>↗</span>
                    </a>
                  )}

                  {demand.link_pncp && (
                    <a
                      href={demand.link_pncp}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600/40 text-blue-400 hover:text-blue-300 border border-blue-500/30 font-semibold text-[11px] transition shadow-sm"
                      title={demand.link_pncp.includes('?q=') ? "Demanda em Planejamento (PLAC 2027): Consultar acervo oficial de contratações da Telebras no PNCP" : "Abrir Contrato Oficial no Portal Nacional de Contratações Públicas (PNCP)"}
                    >
                      <span>🌐 {demand.link_pncp.includes('?q=') ? "Consultar no PNCP" : "Ver no PNCP"}</span>
                      <span>↗</span>
                    </a>
                  )}
                </div>
              </div>

              {/* Painel de Tramitação Atual: Setor, Onde Encontrar e Com Quem Está */}
              <div className="bg-slate-900/80 border border-slate-750 p-3 rounded-lg grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-0.5">
                    🏛️ Setor / Área Atual:
                  </span>
                  <span className="text-white font-medium">{demand.setor_atual || 'Área Demandante'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-0.5">
                    📍 Onde Encontrar:
                  </span>
                  <span className="text-slate-300">{demand.localizacao_atual || 'Mesa Virtual SIGA'}</span>
                </div>
                <div>
                  <span className="text-[10px] text-slate-400 uppercase font-bold block mb-0.5">
                    👤 Com Quem Está:
                  </span>
                  <span className="text-amber-400 font-semibold">
                    {demand.custodiante_atual || demand.responsible_name || 'Responsável Designado'}
                    {demand.dias_no_setor ? (
                      <span className="text-slate-400 font-normal ml-1">({demand.dias_no_setor} dias)</span>
                    ) : null}
                  </span>
                </div>
                {demand.ultimo_despacho_siga && (
                  <div className="md:col-span-3 pt-1.5 border-t border-slate-800 text-[11px] text-slate-400">
                    <strong className="text-slate-300">Último Despacho / Evento SIGA:</strong> {demand.ultimo_despacho_siga}
                  </div>
                )}
              </div>
              {demand.status === 'DEVOLVIDO_AJUSTES' && (
                <div className="space-y-2">
                  {demand.rejection_reason && (
                    <div className="p-3 bg-red-950/40 border border-red-500/30 rounded-lg text-xs text-red-300 flex items-start gap-2">
                      <span className="font-bold text-red-400 shrink-0">Motivo da Devolução:</span>
                      <span>{demand.rejection_reason}</span>
                    </div>
                  )}
                  <div className="flex justify-end pt-1">
                    <button
                      onClick={() => onEditDemandClick && onEditDemandClick(demand)}
                      className="px-4 py-2 bg-gradient-to-r from-red-600 to-amber-600 hover:from-red-700 hover:to-amber-700 text-white font-semibold text-xs rounded-lg transition shadow flex items-center gap-1.5"
                    >
                      <span>✏️</span>
                      <span>Ajustar Proposta e Reenviar</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
      {sigaModalProcesso && (
        <SigaDocumentsModal processo={sigaModalProcesso} onClose={() => setSigaModalProcesso(null)} />
      )}
      {certidaoModalDemandId && (
        <CertidaoVinculacaoModal
          demandId={certidaoModalDemandId}
          onClose={() => setCertidaoModalDemandId(null)}
          onUpdated={() => {
            // Callback opcional após vinculação
          }}
        />
      )}
    </div>
  );
}
