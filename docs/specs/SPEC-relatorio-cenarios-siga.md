# Especificação Técnica Refinada: Relatório Estatístico de Cenários e Prazos do SIGA (Telebras)

## 1. Arquitetura de Governança das Contratações (3 Macrofases)
1. **Fase de Planejamento Estratégico:** Vai da concepção da necessidade (DFD/DOD) até a aprovação e publicação do Calendário de Contratações (PLAC) pela Diretoria Executiva (REDIR).
2. **Fase de Gestão Contratual (Esteira da GCC):** Inicia-se na recepção formal do processo pela GCC para instrução e estende-se **até a Assinatura do Contrato ou emissão da Ordem de Compra (OC) substitutiva**. A homologação do certame é tratada como marco intermediário da fase externa.
3. **Fase de Fiscalização:** Compreende o ciclo pós-assinatura (designação formal de gestores e fiscais via DEG, cadastro no SAP, publicação de extrato no DOU/PNCP, execução e medição contratual).

## 2. Metodologia Estatística e Parâmetros
- **Marco Inicial:** Data de recebimento formal na GCC (`DATA RECEBIDO` / `Data inicio processo`).
- **Marco Final da Fase de Gestão Contratual:** Data de Assinatura do Contrato (`DATA ASSINATURA`) ou emissão da Ordem de Compra substitutiva (`DATA EMISSÃO OC`). Desconsidera-se a data de homologação como término do ciclo de contratação.
- **Nível de Confiança ($1 - \alpha$):** 99,0% ($z = 2,5758$).
- **Margem de Erro Amostral Relativo ($E$):** 2,0% ($\pm 0,02$).
- **Métricas:** Média ($\bar{X}$), Mediana ($\tilde{X}$), Desvio Padrão ($s$), Variância ($s^2$), Erro Padrão da Média ($SE = s / \sqrt{n}$), Intervalo de Confiança ($IC_{99\%} = \bar{X} \pm z \cdot SE$) e Z-Score ($z_i = (x_i - \bar{X}) / s$).

## 3. Correções Tipográficas e Visuais no PDF
- Substituição de caracteres unicode especiais que causam glifos corrompidos (`x■`) na biblioteca ReportLab com fonte Helvetica.
- Uso de notação limpa e compatível:
  - Média: `Média (X̄)` ou `Média (X_bar)`
  - Mediana: `Mediana (X_med)`
  - Erro Padrão: `SE = s / raiz(n)`
  - Intervalo de Confiança: `IC 99% = [ X_bar - (2,5758 * SE) ; X_bar + (2,5758 * SE) ]`

## 4. Reestruturação dos Fluxogramas em Raias (Swimlanes)
- O fluxograma visual deve explicitar verticalmente as 3 macrofases de governança:
  1. *Fase 1: Planejamento Estratégico* (DFD -> Calendário do PLAC)
  2. *Fase 2: Gestão Contratual* (Instrução -> Pesquisa -> Parecer CONJUR -> Disputa Compras.gov -> Homologação -> Coleta de Documentos / Regularidade -> **Assinatura do Contrato / Ordem de Compra**)
  3. *Fase 3: Fiscalização* (Designação DEG -> Cadastro SAP -> Publicação DOU/PNCP -> Medição e Gestão)
- Trajetórias comparadas: Melhor Caso (Fast Track), Caso Esperado Real (Mediana P50) e Pior Caso Outlier (Múltiplas Impugnações / Desvios Graves).

## 5. Estrutura dos Entregáveis
- `RELATORIO_ESTATISTICO_CENARIOS_SIGA_TELEBRAS.xlsx` (6 abas atualizadas até Contrato/OC).
- `RELATORIO_EXECUTIVO_CENARIOS_SIGA_TELEBRAS.pdf` (Documento executivo atualizado com tipografia matemática corrigida e fluxogramas das 3 macrofases).
