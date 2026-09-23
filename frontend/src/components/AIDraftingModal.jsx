import React, { useState, useEffect } from 'react';

export default function AIDraftingModal({ demand, onClose }) {
  const [step, setStep] = useState(0);
  const [typedContent, setTypedContent] = useState('');

  const steps = [
    { msg: 'Iniciando assistente de planejamento IA...', delay: 1000 },
    { msg: 'Buscando histórico do CATMAT/CATSER e contratações similares...', delay: 1500 },
    { msg: 'Acessando templates de ETP (Estudo Técnico Preliminar)...', delay: 1000 },
    { msg: 'Redigindo justificativas baseadas na necessidade informada...', delay: 2000 },
    { msg: 'Gerando Termo de Referência...', delay: 1500 },
    { msg: 'Pronto.', delay: 500 }
  ];

  const generatedMarkdown = `
# Estudo Técnico Preliminar (ETP) - Gerado por IA
**Documento Preliminar para Revisão Humana**

## 1. Descrição da Necessidade
A contratação visa atender à demanda de **${demand.item_type || 'BEM/SERVIÇO'}** para a diretoria, especificamente focada em:
*${demand.description}*

## 2. Previsão no Plano Anual de Contratações
Esta demanda encontra-se alinhada ao Planejamento Estratégico (PEI), com nível de prioridade **${demand.priority_level}** e impacto previsto. O orçamento estimado de **R$ ${Number(demand.estimated_value).toLocaleString('pt-BR')}** foi consultado nas bases históricas.

## 3. Requisitos da Contratação
- O fornecedor deverá comprovar a aderência ao catálogo **CATMAT/CATSER: ${demand.catmat_code || 'Não informado'}**.
- Prazos e critérios de sustentabilidade deverão seguir a IN 05/2017 e a Lei 14.133/2021.

## 4. Termo de Referência (Esboço)
* **Objeto:** Aquisição/Contratação descrita acima.
* **Justificativa:** Necessidade de garantir a continuidade operacional sem ferir o princípio da economicidade.
* **Critérios de Aceitação:** Inspeção visual e técnica no recebimento definitivo...
`;

  useEffect(() => {
    let currentStep = 0;
    
    const runSteps = async () => {
      for (const s of steps) {
        setStep(currentStep);
        await new Promise(r => setTimeout(r, s.delay));
        currentStep++;
      }
      
      // Simulate typing effect
      let i = 0;
      const typeInterval = setInterval(() => {
        setTypedContent(generatedMarkdown.slice(0, i));
        i += 10;
        if (i >= generatedMarkdown.length) {
          clearInterval(typeInterval);
          setTypedContent(generatedMarkdown);
        }
      }, 20);
    };

    runSteps();
  }, []);

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
            <p className="text-xs text-slate-400">Rascunho de Planejamento da Contratação</p>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition text-2xl font-light">×</button>
        </div>

        {/* Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-slate-900/50">
          
          <div className="flex items-center gap-3 p-3 bg-blue-900/10 border border-blue-900/30 rounded-lg">
            <div className="text-2xl">🤖</div>
            <div className="text-sm text-blue-200">
              Estou ajudando a estruturar os documentos preparatórios para a demanda <strong className="text-white">#{demand.id}</strong>.
            </div>
          </div>

          {/* Loader Steps */}
          {step < steps.length - 1 && (
            <div className="space-y-2 p-4 bg-slate-800/50 rounded-lg border border-slate-700 font-mono text-xs text-slate-400">
              {steps.map((s, index) => (
                <div key={index} className={`flex items-center gap-2 ${index > step ? 'opacity-20' : index === step ? 'text-blue-400 animate-pulse' : 'text-emerald-400'}`}>
                  <span>{index < step ? '✓' : index === step ? '⚙' : '○'}</span>
                  {s.msg}
                </div>
              ))}
            </div>
          )}

          {/* Output Document */}
          {step >= steps.length - 1 && (
            <div className="prose prose-invert prose-sm max-w-none">
              <div className="p-6 bg-slate-800 border border-slate-700 rounded-lg shadow-inner whitespace-pre-wrap font-sans text-slate-300">
                {typedContent}
                {typedContent.length < generatedMarkdown.length && (
                  <span className="inline-block w-2 h-4 bg-blue-500 animate-pulse ml-1 align-middle"></span>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900 flex justify-end gap-3">
          <button onClick={onClose} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium rounded-lg transition">
            Fechar
          </button>
          <button 
            disabled={typedContent.length < generatedMarkdown.length}
            className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 text-white text-sm font-medium rounded-lg shadow transition"
          >
            Aprovar Rascunho
          </button>
        </div>
      </div>
    </div>
  );
}
