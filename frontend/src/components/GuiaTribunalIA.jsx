import React from 'react';

export default function GuiaTribunalIA() {
  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-6 shadow-xl text-slate-200 space-y-6">
      {/* Header do Guia */}
      <div className="border-b border-slate-700 pb-4">
        <div className="flex items-center gap-3">
          <span className="text-3xl">📖</span>
          <div>
            <h2 className="text-xl font-bold text-white">Manual Prático: Como Usar o Tribunal da IA para Enquadramento Legal</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Diretrizes de Instrução Processual, Blindagem de Riscos e Jurisprudência do TCU (Lei nº 14.133/2021 e Lei nº 13.303/2016)
            </p>
          </div>
        </div>
      </div>

      {/* Seção 1: O que é o Tribunal da IA */}
      <div className="bg-slate-900/80 border border-blue-500/30 rounded-lg p-4 space-y-2">
        <h3 className="text-sm font-bold text-blue-400 flex items-center gap-2">
          <span>🏛️</span> 1. O que é o Tribunal da IA e por que utilizá-lo?
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          O <strong>Tribunal da IA</strong> atua como um colegiado preliminar inteligente para a área demandante. Antes de formalizar o processo na GCC ou na DAFRI, a IA analisa a pretensão da contratação sob a ótica de três pareceristas simultâneos:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
          <div className="bg-slate-800/80 p-3 rounded border border-slate-700 text-xs">
            <p className="font-bold text-emerald-400 mb-1">👨‍⚖️ Juiz Relator</p>
            <p className="text-slate-400">Classifica a modalidade correta (Dispensa, Inexigibilidade, Credenciamento ou Pregão) e aponta o Artigo e Inciso do PNCP.</p>
          </div>
          <div className="bg-slate-800/80 p-3 rounded border border-slate-700 text-xs">
            <p className="font-bold text-amber-400 mb-1">🛡️ Auditor de Riscos TCU</p>
            <p className="text-slate-400">Audita risco de fracionamento de despesa, validade de atestados de exclusividade (Súmula 255) e pesquisa de preços (Art. 23).</p>
          </div>
          <div className="bg-slate-800/80 p-3 rounded border border-slate-700 text-xs">
            <p className="font-bold text-purple-400 mb-1">📋 Assessor Técnico</p>
            <p className="text-slate-400">Redige o objeto no padrão PNCP, elabora a justificativa da contratação, calcula as vigências e estrutura os itens.</p>
          </div>
        </div>
      </div>

      {/* Seção 2: Árvore de Decisão Rápida */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <span>🌳</span> 2. Árvore de Decisão: Qual Modalidade Devo Utilizar?
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Card Inexigibilidade */}
          <div className="bg-slate-900 border-l-4 border-red-500 p-4 rounded-r-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-red-400 text-sm">Inexigibilidade de Licitação (ID 9)</span>
              <span className="text-[10px] bg-red-950 text-red-300 px-2 py-0.5 rounded border border-red-800">Inviabilidade de Competição</span>
            </div>
            <p className="text-xs text-slate-300">
              <strong>Quando cabe:</strong> Quando a competição for juridicamente ou faticamente impossível.
            </p>
            <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
              <li><strong>Fornecedor Exclusivo (Art. 74, I / Art. 30, I):</strong> Só há um fabricante ou representante. <span className="text-red-300 font-semibold">Exige Atestado da ABES, Sindicato ou Federação do Comércio (Súmula 255/TCU).</span></li>
              <li><strong>Notória Especialização (Art. 74, II / Art. 30, II):</strong> Serviços técnicos singulares intelectuais (pareceres, consultorias de alto nível, treinamentos singulares).</li>
            </ul>
          </div>

          {/* Card Dispensa */}
          <div className="bg-slate-900 border-l-4 border-amber-500 p-4 rounded-r-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-amber-400 text-sm">Dispensa de Licitação (ID 8)</span>
              <span className="text-[10px] bg-amber-950 text-amber-300 px-2 py-0.5 rounded border border-amber-800">Competição Viável, mas Dispensada</span>
            </div>
            <p className="text-xs text-slate-300">
              <strong>Quando cabe:</strong> A licitação é possível, mas a lei autoriza a contratação direta.
            </p>
            <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
              <li><strong>Por Valor (Art. 75, II / Art. 29, II):</strong> Compras e serviços até R$ 59.906,02.</li>
              <li><strong>Obras/Engenharia (Art. 75, I / Art. 29, I):</strong> Obras e serviços de engenharia até R$ 119.812,02.</li>
              <li><strong>Emergência (Art. 75, VIII):</strong> Urgência concreta para evitar dano irreparável.</li>
            </ul>
          </div>

          {/* Card Credenciamento */}
          <div className="bg-slate-900 border-l-4 border-blue-500 p-4 rounded-r-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-blue-400 text-sm">Credenciamento (ID 10)</span>
              <span className="text-[10px] bg-blue-950 text-blue-300 px-2 py-0.5 rounded border border-blue-800">Procedimento Auxiliar (Art. 79)</span>
            </div>
            <p className="text-xs text-slate-300">
              <strong>Quando cabe:</strong> Todos os prestadores que atenderem aos requisitos do edital podem ser contratados simultaneamente.
            </p>
            <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
              <li><strong>Paralelo e não excludente (Art. 79, I):</strong> Clínicas médicas, postos de combustíveis, peritos, leiloeiros.</li>
              <li><strong>Seleção a critério do usuário (Art. 79, II):</strong> O beneficiário do serviço escolhe o credenciado de sua preferência.</li>
            </ul>
          </div>

          {/* Card Pregão */}
          <div className="bg-slate-900 border-l-4 border-emerald-500 p-4 rounded-r-lg space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-bold text-emerald-400 text-sm">Pregão Eletrônico (ID 6)</span>
              <span className="text-[10px] bg-emerald-950 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">Regra Geral Obrigatória</span>
            </div>
            <p className="text-xs text-slate-300">
              <strong>Quando cabe:</strong> Aquisição de bens e serviços comuns acima do limite de dispensa e com mercado amplo.
            </p>
            <ul className="text-xs text-slate-400 list-disc list-inside space-y-1">
              <li>Padrões de desempenho objetivamente definidos por especificações usuais de mercado.</li>
              <li>Critério de menor preço ou maior desconto, com disputa em sessão pública no Compras.gov.br.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Seção 3: Cuidados Críticos perante o TCU */}
      <div className="bg-red-950/40 border border-red-500/40 rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-bold text-red-400 flex items-center gap-2">
          <span>⚠️</span> 3. As 3 Regras de Ouro para Blindagem perante o TCU e CGU
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
          <div className="space-y-1 bg-slate-900/60 p-3 rounded border border-slate-700">
            <p className="font-bold text-amber-300">1. Vedação ao Fracionamento</p>
            <p className="text-slate-400">
              O Art. 75, § 1º da Lei 14.133 proíbe dividir compras de mesma natureza para fugir da licitação. O limite de R$ 59.906,02 é <strong>global para o ano todo</strong> na mesma unidade.
            </p>
          </div>
          <div className="space-y-1 bg-slate-900/60 p-3 rounded border border-slate-700">
            <p className="font-bold text-amber-300">2. Atestado de Exclusividade Real</p>
            <p className="text-slate-400">
              Súmula 255 do TCU: Carta de exclusividade emitida pela própria empresa ou declaração simples não é aceita. Exige-se certidão de entidade comercial ou sindicato patronal.
            </p>
          </div>
          <div className="space-y-1 bg-slate-900/60 p-3 rounded border border-slate-700">
            <p className="font-bold text-amber-300">3. Pesquisa Formal de Preços</p>
            <p className="text-slate-400">
              Mesmo na Inexigibilidade ou Dispensa, a razoabilidade do preço deve ser comprovada (Art. 23 da Lei 14.133 ou IN SEGES 65/2021) com base em notas fiscais de outros órgãos.
            </p>
          </div>
        </div>
      </div>

      {/* Seção 4: Passo a Passo no Sistema */}
      <div className="bg-slate-900/60 p-4 rounded-lg border border-slate-700 space-y-2">
        <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
          <span>🚀</span> 4. Passo a Passo para a Área Demandante
        </h3>
        <ol className="text-xs text-slate-300 list-decimal list-inside space-y-2">
          <li>Acesse a aba <strong>"⚖️ Tribunal da IA (Julgamento)"</strong> e descreva o objeto com suas palavras.</li>
          <li>Informe o valor orçado aproximado e selecione se há exclusividade ou notória especialização.</li>
          <li>Clique em <strong>"⚖️ Julgar Enquadramento com Tribunal da IA"</strong> para obter os pareceres do Relator, do Auditor TCU e do Assessor.</li>
          <li>Revise os alertas de risco do TCU e o checklist obrigatório.</li>
          <li>Clique no botão <strong>"📥 Aplicar no Formulário de Compra"</strong>: todos os campos da compra (Objeto, Justificativa, Artigo/Inciso PNCP, Vigências e Itens) serão preenchidos automaticamente.</li>
          <li>Revise os itens e anexe o documento ou ETP preliminar, finalizando o registro com <strong>"Salvar na Gestão de Demandas"</strong>.</li>
        </ol>
      </div>
    </div>
  );
}
