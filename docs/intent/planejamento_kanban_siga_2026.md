# Declaração de Intenção: Refatoração da Gestão de Planejamento (Kanban SIGA 2026)

**Data de Confirmação:** 30/09/2026  
**Status:** Confirmado pelo Usuário (`interview-me`)  
**Iniciativa:** Rastreamento Integral dos Processos em Tramitação na Fase de Planejamento da Telebras

---

## 1. Declaração Estruturada de Intenção (Statement of Intent)

* **Outcome:** Relatório Executivo em PDF e Planilha analítica em Excel contendo o inventário e telemetria de **todos os processos em tramitação no SIGA previstos para contratação ainda em 2026 que se encontram na fase de planejamento**, cruzados com os PLACs 2023–2026 (ou classificados como extraordinários/não planejados), estruturados segundo o modelo conceitual de esteira Kanban com: localização física/setorial no SIGA, custodiante atual (com quem está), ação em andamento (o que estão fazendo), tempo decorrido no setor vs. prazos médios de tramitação, análise crítica de gargalos e histórico detalhado de documentos produzidos e em elaboração no processo eletrônico.
* **User:** Gestores de Contratação, Diretorias Requisitantes (DAFRI, DTO, DGOV, Presidência) e a GCC (Gerência de Compras e Contratos) da Telebras, permitindo o acompanhamento em tempo real das movimentações entre a área demandante e todos os setores intervenientes.
* **Why now:** Assegurar que as contratações com previsão de fechamento e execução ainda em 2026 não sofram apagão ou atraso por inércia oculta nas áreas demandantes e no SIGA, trazendo clareza visual e telemetria gerencial antes de intervir no sistema.
* **Success:** Entrega prévia e imediata do Relatório Oficial em PDF (padrão Telebras de alta fidelidade) e da Planilha analítica em Excel com a base integral dos processos ativos de planejamento e suas métricas de tramitação, servindo de base formal para a gestão avaliar e homologar as regras antes da refatoração do software.
* **Constraint (Inviolável):** **Nenhuma linha de código** (backend ou frontend) será alterada antes da geração, análise e validação desse relatório em PDF e da planilha em Excel.
* **Out of scope:** Alterações no código da aplicação neste momento, bem como processos que já superaram o planejamento e já se encontram em sessão pública de licitação ou em fase de execução contratual.

---

## 2. Princípios de Modelagem do Kanban de Planejamento

1. **Segregação por Macro-Fases do Planejamento:**
   - Coluna 1: *Autuação da Demanda & DFD* (Área Demandante)
   - Coluna 2: *Elaboração do ETP & Matriz de Riscos* (Equipe Técnica de Planejamento)
   - Coluna 3: *Pesquisa de Preços IN 65/2021 & Termo de Referência/Projeto Básico* (Pesquisa & Validação)
   - Coluna 4: *Análise Prévia & Parecer Jurídico* (CONJUR / Diligências de Saneamento)
   - Coluna 5: *Triagem, Conformidade & Homologação GCC* (Calendário e Prontidão para Certame)
2. **Telemetria de Gargalos:**
   - Comparação paramétrica do tempo de permanência no setor atual contra a meta de referência (ex.: ETP limite de 35 dias úteis, DFD limite de 10 dias úteis, Triagem GCC limite de 10 dias úteis).
   - Sinalização de alertas para processos estagnados ou em devolução para saneamento.
3. **Histórico Documental no SIGA:**
   - Registro de peças essenciais juntadas (DFD, ETP, Matriz de Riscos, RMS SAP, Pesquisa de Preços, Minuta de Edital/TR, Pareceres) e indicação do próximo documento pendente para destravar o processo.
