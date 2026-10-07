# Capability Map: Painel de Planejamento e Capacidade PLAC (Telebras)

## Iniciativa
Estruturação da governança, inteligência e fiscalização do ciclo de planejamento de contratações do PLAC da Telebras, integrando o agendamento inteligente da capacidade da GCC, amarração com o SIGA via Certidão com Código de Rastreio e fiscalização autônoma de prazos.

## Matriz de Módulos e Dependências

| Módulo ID | Responsabilidade | Depende de | Status |
|---|---|---|:---:|
| **planejamento-capacidade** | Motor de agendamento reverso (dias úteis das 10 esteiras GCC), balanceamento de carga da equipe de compras por quadrimestre (Q1, Q2, Q3) e recomendação de janelas cabíveis/slots livres para novas demandas. | — | Concluído e Testado |
| **certidao-rastreio** | Emissão da Certidão Oficial do PLAC em PDF, motor do Código de Rastreio (PLAC-[ANO]-[AREA]+[NUMERO]), e lógica de amarração com o processo autuado no SIGA (TLB-PRO). | planejamento-capacidade | Concluído e Testado |
| **esteira-governanca** | Interface visual em Kanban das fases de aprovação (Levantamento -> Validação Diretor -> Consolidação GCC -> Deliberação REDIR -> Calendário) com filtros por Quadrimestre (Q1, Q2, Q3) e semáforo de sobrecarga. | certidao-rastreio | Concluído e Testado |
| **robo-monitor-planejamento** | Sentinela automatizado de conformidade que apura os indicadores oficiais da Telebras (IAC - Aderência ao Calendário, ICNP - Contratações Não Planejadas, TEP - Taxa de Execução, TMP - Tempo Médio) e fiscaliza quem cumpre o plano vs. quem empurra urgência fabricada. | esteira-governanca | Concluído e Testado |
| **autenticacao-oauth** | Autenticação corporativa via OAuth 2.0 / OIDC (Entra ID / Gov.br / Keycloak), provisionamento Just-in-Time (JIT), RBAC e emissão de JWT compatível com o ecossistema existente. | — | Concluído e Testado |

