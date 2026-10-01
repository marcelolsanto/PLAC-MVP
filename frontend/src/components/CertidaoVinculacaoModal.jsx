import React, { useState, useEffect } from 'react';
import api from '../services/api';

export default function CertidaoVinculacaoModal({ demandId, initialSigaNumber = '', onClose, onUpdated }) {
  const [loading, setLoading] = useState(true);
  const [dados, setDados] = useState(null);
  const [numeroSiga, setNumeroSiga] = useState(initialSigaNumber);
  const [salvando, setSalvando] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [copiado, setCopiado] = useState(false);
  const [baixandoPdf, setBaixandoPdf] = useState(false);

  useEffect(() => {
    carregarDados();
  }, [demandId]);

  const carregarDados = async () => {
    try {
      setLoading(true);
      const res = await api.get(`/planejamento/demandas/${demandId}/certidao-dados/`);
      setDados(res.data);
      if (res.data.siga_process_number) {
        setNumeroSiga(res.data.siga_process_number);
      }
    } catch (err) {
      console.error('Erro ao carregar dados da certidão:', err);
      setFeedback({ tipo: 'erro', msg: 'Erro ao carregar dados da demanda.' });
    } finally {
      setLoading(false);
    }
  };

  const handleVincularSiga = async (e) => {
    e.preventDefault();
    if (!numeroSiga.trim()) {
      setFeedback({ tipo: 'erro', msg: 'Informe o número do processo SIGA.' });
      return;
    }

    try {
      setSalvando(true);
      setFeedback(null);
      const res = await api.post('/planejamento/vincular-processo-siga/', {
        demand_id: demandId,
        numero_processo_siga: numeroSiga.trim()
      });

      setFeedback({ tipo: 'sucesso', msg: res.data.mensagem });
      if (res.data.siga_process_number) {
        setNumeroSiga(res.data.siga_process_number);
      }
      if (onUpdated) {
        onUpdated(res.data);
      }
    } catch (err) {
      const msg = err.response?.data?.mensagem || 'Falha ao vincular processo SIGA.';
      setFeedback({ tipo: 'erro', msg });
    } finally {
      setSalvando(false);
    }
  };

  const copiarCodigo = () => {
    if (dados?.codigo_rastreio_plac) {
      navigator.clipboard.writeText(dados.codigo_rastreio_plac);
      setCopiado(true);
      setTimeout(() => setCopiado(false), 2500);
    }
  };

  const baixarPdf = async () => {
    try {
      setBaixandoPdf(true);
      setFeedback(null);
      const res = await api.get(`/planejamento/demandas/${demandId}/emitir-certidao-pdf/`, {
        responseType: 'blob'
      });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = downloadUrl;
      const codigo = dados?.codigo_rastreio_plac || demandId;
      link.setAttribute('download', `Certidao_PLAC_${codigo}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err) {
      console.error('Erro ao baixar certidão PDF via Blob:', err);
      try {
        const directUrl = `http://${window.location.hostname}:8085/api/planejamento/demandas/${demandId}/emitir-certidao-pdf/`;
        const link = document.createElement('a');
        link.href = directUrl;
        link.setAttribute('download', `Certidao_PLAC_${demandId}.pdf`);
        link.target = '_blank';
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (fallbackErr) {
        setFeedback({ tipo: 'erro', msg: 'Erro ao gerar ou baixar o arquivo PDF da certidão.' });
      }
    } finally {
      setBaixandoPdf(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto animate-fadeIn">
      <div className="bg-slate-900 border border-slate-750 w-full max-w-3xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header Modal */}
        <div className="bg-slate-850 px-6 py-4 border-b border-slate-750 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-600/20 text-blue-400 border border-blue-500/30 flex items-center justify-center text-lg">
              📄
            </div>
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                Certidão Oficial de Planejamento e Conformidade PLAC
              </h3>
              <p className="text-xs text-slate-400">
                Peça nº 01 do processo administrativo no SIGA e chave de auditoria robótica
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white text-lg p-1.5 rounded-lg hover:bg-slate-750 transition"
          >
            ✕
          </button>
        </div>

        {/* Conteúdo */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1 text-slate-200 text-xs">
          {loading ? (
            <div className="py-20 text-center text-slate-400 space-y-3">
              <div className="animate-spin text-3xl">⚙️</div>
              <p className="text-xs">Gerando certidão e calculando hash de integridade...</p>
            </div>
          ) : dados ? (
            <>
              {/* Box Institucional do Código de Rastreio */}
              <div className="bg-gradient-to-r from-blue-950/60 via-indigo-950/40 to-slate-900 border-2 border-blue-500/60 rounded-2xl p-5 text-center space-y-2 relative shadow-lg">
                <span className="text-[10px] uppercase font-mono tracking-widest text-blue-400 font-bold">
                  Código de Rastreio de Gestão Oficial
                </span>
                <div className="text-2xl font-black text-white font-mono flex items-center justify-center gap-3">
                  <span>{dados.codigo_rastreio_plac}</span>
                  <button
                    onClick={copiarCodigo}
                    className="text-xs px-2.5 py-1 bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 rounded-lg border border-blue-500/40 transition font-sans font-medium"
                  >
                    {copiado ? '✓ Copiado!' : 'Copiar'}
                  </button>
                </div>
                <p className="text-[11px] text-slate-300 max-w-lg mx-auto">
                  Este código <strong>DEVE ser referenciado no campo Assunto</strong> na autuação do processo no SIGA para que o Robô Especialista acompanhe os trâmites.
                </p>
              </div>

              {/* Ficha Resumida da Demanda */}
              <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
                <h4 className="font-bold text-white text-xs uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                  <span>🏛️</span> Dados da Contratação (Diretoria & Objeto)
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div>
                    <span className="text-slate-400 text-[11px]">Diretoria / Gerência:</span>
                    <p className="font-semibold text-white">{dados.diretoria} • {dados.gerencia}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[11px]">Responsável pelo Registro:</span>
                    <p className="font-semibold text-white">{dados.responsavel_nome} ({dados.responsavel_email})</p>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-slate-400 text-[11px]">Objeto da Contratação:</span>
                    <p className="font-medium text-slate-200 mt-0.5">{dados.objeto}</p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[11px]">Valor Estimado Global:</span>
                    <p className="font-bold text-emerald-400 text-sm">
                      {new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(dados.valor_estimado || 0)}
                    </p>
                  </div>
                  <div>
                    <span className="text-slate-400 text-[11px]">Data Pretendida de Assinatura:</span>
                    <p className="font-bold text-white text-sm font-mono">
                      {dados.data_pretendida_assinatura ? dados.data_pretendida_assinatura.split('-').reverse().join('/') : 'Não informada'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Cronograma Reverso e Prazos Regimentais */}
              {dados.cronograma_reverso && (
                <div className="bg-slate-950/70 border border-slate-800 rounded-xl p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="font-bold text-white text-xs uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                      <span>⏱️</span> Cronograma Reverso Regimental (SLA da GCC)
                    </h4>
                    <span className="text-[11px] font-mono text-amber-400 font-bold">
                      {dados.cronograma_reverso.quadrimestre_alvo}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5 pt-1">
                    <div className="p-3 bg-rose-950/30 border border-rose-500/40 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase font-mono block">Data Fatal Abertura SIGA</span>
                      <span className="text-sm font-bold text-rose-300 font-mono block mt-0.5">
                        {dados.cronograma_reverso.data_fatal_abertura_siga.split('-').reverse().join('/')}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-1">Limite máximo para a área</span>
                    </div>

                    <div className="p-3 bg-slate-900 border border-slate-750 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase font-mono block">Data-Limite Envio GCC</span>
                      <span className="text-sm font-bold text-amber-300 font-mono block mt-0.5">
                        {dados.cronograma_reverso.data_limite_envio_gcc.split('-').reverse().join('/')}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-1">ETP/TR saneado</span>
                    </div>

                    <div className="p-3 bg-emerald-950/30 border border-emerald-500/40 rounded-lg">
                      <span className="text-[10px] text-slate-400 uppercase font-mono block">Assinatura / Homologação</span>
                      <span className="text-sm font-bold text-emerald-300 font-mono block mt-0.5">
                        {dados.cronograma_reverso.data_pretendida_assinatura.split('-').reverse().join('/')}
                      </span>
                      <span className="text-[10px] text-slate-400 block mt-1">Prazo: {dados.cronograma_reverso.sla_regimental_gcc_dias_uteis}d úteis</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Botão de Download do PDF Oficial */}
              <div className="flex flex-col items-center gap-2 pt-1">
                <button
                  type="button"
                  onClick={baixarPdf}
                  disabled={baixandoPdf}
                  className="bg-blue-600 hover:bg-blue-500 disabled:opacity-60 disabled:cursor-not-allowed text-white font-bold text-xs py-3 px-6 rounded-xl shadow-lg shadow-blue-600/30 transition flex items-center gap-2"
                >
                  <span className={baixandoPdf ? 'animate-spin' : ''}>{baixandoPdf ? '⏳' : '📥'}</span>
                  <span>{baixandoPdf ? 'Gerando Certidão em PDF...' : 'Baixar Certidão Oficial em PDF (Peça nº 01 do SIGA)'}</span>
                </button>
                <a
                  href={`http://${typeof window !== 'undefined' ? window.location.hostname : '100.95.28.45'}:8085/api/planejamento/demandas/${demandId}/emitir-certidao-pdf/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[11px] text-blue-400 hover:text-blue-300 underline underline-offset-2 transition"
                >
                  Ou clique aqui para download direto (Porta 8085)
                </a>
              </div>

              {/* Bloco de Vinculação com o Processo SIGA (A Ponte) */}
              <div className="bg-slate-850 border border-slate-700 rounded-xl p-5 space-y-4">
                <div className="flex items-center gap-2.5">
                  <span className="text-xl">🔗</span>
                  <div>
                    <h4 className="font-bold text-white text-xs">
                      Amarração com o Processo do SIGA (Process Binding)
                    </h4>
                    <p className="text-[11px] text-slate-400">
                      Informe o número do processo gerado após a autuação no SIGA para ativar o Robô de Gestão Contratual.
                    </p>
                  </div>
                </div>

                <form onSubmit={handleVincularSiga} className="flex flex-col sm:flex-row gap-3">
                  <input
                    type="text"
                    value={numeroSiga}
                    onChange={(e) => setNumeroSiga(e.target.value)}
                    placeholder="Ex: TLB-PRO-2026/002672"
                    className="flex-1 bg-slate-950 border border-slate-750 text-white rounded-xl px-3.5 py-2.5 text-xs font-mono uppercase focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 outline-none"
                  />
                  <button
                    type="submit"
                    disabled={salvando}
                    className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs py-2.5 px-5 rounded-xl transition shadow flex items-center justify-center gap-2 shrink-0 disabled:opacity-50"
                  >
                    {salvando ? 'Salvando...' : '🔗 Vincular Processo SIGA'}
                  </button>
                </form>

                {feedback && (
                  <div className={`p-3 rounded-lg text-xs font-medium flex items-center gap-2 ${
                    feedback.tipo === 'sucesso'
                      ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-500/40'
                      : 'bg-rose-950/80 text-rose-300 border border-rose-500/40'
                  }`}>
                    <span>{feedback.tipo === 'sucesso' ? '✓' : '⚠️'}</span>
                    <span>{feedback.msg}</span>
                  </div>
                )}
              </div>

              {/* Hash e Rodapé de Autenticidade */}
              <div className="text-center pt-2 space-y-1">
                <span className="text-[10px] font-mono text-slate-500 block">
                  CHAVE SHA-256: {dados.hash_autenticidade_sha256}
                </span>
                <span className="text-[10px] text-slate-500 block">
                  Autenticidade garantida pelo Sistema de Planejamento e Inteligência PLAC — Telebras.
                </span>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}
