import React, { useState, useEffect, useRef } from 'react';

export default function AIDraftingModal({ demand, onClose }) {
  const [step, setStep] = useState(0);
  const [typedContent, setTypedContent] = useState('');
  const [isApproved, setIsApproved] = useState(false);
  const [copied, setCopied] = useState(false);
  const timerRef = useRef(null);

  const steps = [
    { msg: 'Iniciando assistente de planejamento IA...', delay: 800 },
    { msg: 'Buscando histórico do CATMAT/CATSER e contratações similares...', delay: 1000 },
    { msg: 'Acessando templates de ETP (Estudo Técnico Preliminar)...', delay: 800 },
    { msg: 'Redigindo justificativas baseadas na necessidade informada...', delay: 1200 },
    { msg: 'Gerando Termo de Referência...', delay: 1000 },
    { msg: 'Documento pronto para análise.', delay: 400 }
  ];

  const generatedMarkdown = `
# Estudo Técnico Preliminar (ETP) - Gerado por IA
**Documento Preliminar para Revisão e Instrução Processual**

---

### 1. Descrição Sucinta da Necessidade
A presente contratação destina-se a atender às demandas de **${demand.item_type || 'BEM/SERVIÇO'}** para o exercício vigente, tendo como objeto:
> "${demand.description}"

### 2. Alinhamento Estratégico & Justificativa
Esta contratação está alinhada ao Plano Estratégico Institucional (PEI) sob a diretriz:
* **Vinculação Estratégica:** ${demand.strategic_alignment || 'Continuidade Operacional e Eficiência'}
* **Grau de Prioridade:** ${demand.priority_level || 'MÉDIO'} (Pontuação Matriz: ${demand.priority_score || 'N/A'} pts)
* **Estimativa Orçamentária Inicial:** R$ ${Number(demand.estimated_value || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}

### 3. Requisitos da Contratação & Catálogo Oficial
* **Código CATMAT/CATSER Identificado:** ${demand.catmat_code || 'A definir na consolidação'}
* **Enquadramento Legal:** Lei Federal nº 14.133/2021 e Diretriz Interna do PLAC.
* **Critérios de Sustentabilidade:** Cumprimento das exigências ambientais e normas ABNT vigentes.

### 4. Esboço do Termo de Referência (TR)
1. **Objeto:** Contratação de solução para suprir a necessidade declarada pela unidade demandante.
2. **Critérios de Aceitação:** Verificação da conformidade com o catálogo e termo de aceite em até 10 (dez) dias úteis.
3. **Prazo de Vigência Contratual:** 12 meses a contar da data de assinatura pretendida (${demand.intended_date ? new Date(demand.intended_date).toLocaleDateString('pt-BR') : 'A definir'}).
`;

  const skipToEnd = () => {
    if (timerRef.current) clearInterval(timerRef.current);
    setStep(steps.length - 1);
    setTypedContent(generatedMarkdown);
  };

  useEffect(() => {
    let currentStep = 0;
    let isCancelled = false;

    const runSteps = async () => {
      for (const s of steps) {
        if (isCancelled) return;
        setStep(currentStep);
        await new Promise(r => setTimeout(r, s.delay));
        currentStep++;
      }
      
      if (isCancelled) return;

      // Typing simulation
      let i = 0;
      timerRef.current = setInterval(() => {
        if (isCancelled) return;
        i += 18;
        if (i >= generatedMarkdown.length) {
          clearInterval(timerRef.current);
          setTypedContent(generatedMarkdown);
        } else {
          setTypedContent(generatedMarkdown.slice(0, i));
        }
      }, 15);
    };

    runSteps();

    return () => {
      isCancelled = true;
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const handleApprove = () => {
    setIsApproved(true);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(typedContent || generatedMarkdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const isReady = step >= steps.length - 1;

  return (
    <div className="fixed inset-0 bg-black/80 flex justify-end z-50 transition-opacity">
      {/* Sidebar Slider Modal */}
      <div className="w-full max-w-2xl bg-slate-900 h-full shadow-2xl border-l border-slate-700 flex flex-col animate-slide-in">
        
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-900 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <span className="text-xl">✨</span> Copilot ETP / TR (IA)
            </h3>
            <p className="text-xs text-slate-400">Rascunho de Planejamento da Contratação • Demanda #{demand.id}</p>
          </div>
          <button 
            onClick={onClose} 
            className="text-slate-400 hover:text-white transition text-2xl font-light px-2"
            title="Fechar modal"
          >
            ×
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-5 bg-slate-900/50">
          
          {/* Status Banner */}
          {isApproved ? (
            <div className="p-4 bg-emerald-500/15 border border-emerald-500/50 rounded-xl text-emerald-300 space-y-2">
              <div className="flex items-center gap-2 font-bold text-sm">
                <span>✅</span>
                <span>Rascunho de ETP / TR Aprovado com Sucesso!</span>
              </div>
              <p className="text-xs text-emerald-400/90 leading-relaxed">
                A minuta preliminar foi validada e vinculada à Demanda <strong>#{demand.id}</strong>. Os dados foram incorporados à esteira de compras para subsidiar a fase preparatória da licitação.
              </p>
            </div>
          ) : (
            <div className="flex items-center justify-between p-3 bg-blue-900/15 border border-blue-900/30 rounded-lg">
              <div className="flex items-center gap-2.5 text-xs text-blue-200">
                <span className="text-xl">🤖</span>
                <span>Estruturando estudo preliminar para <strong>#{demand.id}</strong></span>
              </div>
              {!isReady && (
                <button
                  onClick={skipToEnd}
                  className="text-[11px] bg-slate-800 hover:bg-slate-700 text-blue-400 border border-blue-500/30 px-2.5 py-1 rounded transition"
                >
                  ⏩ Pular Animação
                </button>
              )}
            </div>
          )}

          {/* Loader Steps (while generating) */}
          {!isReady && (
            <div className="space-y-2 p-4 bg-slate-800/50 rounded-lg border border-slate-700 font-mono text-xs text-slate-400">
              {steps.map((s, index) => (
                <div 
                  key={index} 
                  className={`flex items-center gap-2 ${
                    index > step 
                      ? 'opacity-20' 
                      : index === step 
                      ? 'text-blue-400 font-semibold animate-pulse' 
                      : 'text-emerald-400'
                  }`}
                >
                  <span>{index < step ? '✓' : index === step ? '⚙' : '○'}</span>
                  <span>{s.msg}</span>
                </div>
              ))}
            </div>
          )}

          {/* Output Document Preview */}
          {isReady && (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400 px-1">
                <span className="font-semibold uppercase tracking-wider text-[10px]">Minuta Gerada</span>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-2.5 py-1 rounded border border-slate-700 transition text-[11px]"
                >
                  {copied ? '✓ Copiado!' : '📋 Copiar Texto'}
                </button>
              </div>

              <div className="p-5 bg-slate-800 border border-slate-700 rounded-xl shadow-inner whitespace-pre-wrap font-sans text-xs text-slate-200 leading-relaxed max-h-[460px] overflow-y-auto">
                {typedContent}
                {typedContent.length < generatedMarkdown.length && (
                  <span className="inline-block w-2 h-3.5 bg-blue-500 animate-pulse ml-1 align-middle"></span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900 flex justify-end items-center gap-3">
          <button 
            onClick={onClose} 
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium rounded-lg transition"
          >
            {isApproved ? 'Concluir' : 'Cancelar'}
          </button>

          {isApproved ? (
            <button
              onClick={onClose}
              className="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold rounded-lg shadow transition flex items-center gap-1.5"
            >
              <span>✓</span>
              <span>Aprovado & Salvo</span>
            </button>
          ) : (
            <button
              onClick={handleApprove}
              className="px-5 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white text-xs font-semibold rounded-lg shadow transition flex items-center gap-1.5"
            >
              <span>✨</span>
              <span>Aprovar Rascunho</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
