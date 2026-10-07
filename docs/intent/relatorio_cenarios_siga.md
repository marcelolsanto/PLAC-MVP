# Declaração de Intenção Refinada: Relatório de Cenários e Prazos Históricos do SIGA (Telebras)

## 1. Contexto e Macrofases de Governança
O ciclo de vida das contratações públicas na Telebras estrutura-se formalmente em três macrofases distintas:
1. **Fase de Planejamento Estratégico:** Vai desde a identificação da necessidade institucional (DFD/DOD) até a consolidação e aprovação do Calendário de Contratações (PLAC) pela Diretoria Executiva (REDIR) e Conselho.
2. **Fase de Gestão Contratual (Esteira da GCC):** Compreende desde o recebimento formal do processo na Gerência de Compras e Contratos (instrução, pesquisa de preços, Termo de Referência, parecer jurídico, certame licitatório ou processo de dispensa/inexigibilidade, saneamento pós-sessão e formalização) **até a efetiva Assinatura do Contrato ou emissão da Ordem de Compra (OC) substitutiva**.
3. **Fase de Fiscalização:** Inicia-se imediatamente após a assinatura do ajuste / emissão da OC (designação formal de gestores e fiscais via DEG, cadastro no SAP, publicação de extrato no DOU/PNCP, execução e medição contratual).

## 2. Escopo e Métrica Temporal da Modelagem
- **Outcome:** Atualização completa do **Relatório Executivo em PDF** e da **Planilha Excel Modelada**, corrigindo a renderização visual das fórmulas matemáticas (eliminando os glifos corrompidos `x■`), reestruturando os fluxogramas sob as 3 macrofases de governança e recalculando a modelagem estatística para que o marco final seja a **Assinatura do Contrato (ou emissão da Ordem de Compra - OC)**, descartando a homologação como ponto de corte.
- **User:** Gestores de contratações, planejamento e governança da Telebras (GCC, DAFRI e áreas requisitantes).
- **Why now:** Alinhamento rigoroso à Diretriz do PLAC (indicador TMP - Tempo Médio de Processo) e à sistemática corporativa da Telebras, onde a homologação é uma etapa intermediária e o planejamento de compras só se materializa com a celebração do contrato ou expedição da Ordem de Compra.
- **Success Criteria:**
  1. Inferência estatística formal com **Intervalo de Confiança de 99,0%** e **Margem de Erro Amostral de 2,0%**.
  2. Apuração de média, mediana, variância, desvio padrão, erro padrão da média e z-scores do ciclo integral `[Entrada GCC -> Contrato / OC]`.
  3. Fórmulas matemáticas no PDF com tipografia 100% nítida e legível.
  4. Fluxogramas e tabelas explicitando as 3 macrofases de governança corporativa.
  5. Identificação nominal dos novos outliers de maior prazo até a assinatura contratual / OC.
- **Constraints:** Coleta de datas de assinatura de contratos e de ordens de compra no SIGA a partir das planilhas `15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx`, `4. COMPRA POR DISPENSA_INEXIGIBILIDADE.xlsx` e `6. PREGÃO ELETRONICO e DISP. ELETRÔNICA.xlsx`.
- **Out of Scope:** Não abrange a modelagem temporal da Fase de Fiscalização (pós-assinatura), focando estritamente na Fase de Gestão Contratual até a celebração do ajuste.
