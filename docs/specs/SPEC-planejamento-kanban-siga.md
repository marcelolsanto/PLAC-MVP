# Spec: Gestão e Telemetria de Planejamento (Esteira Kanban SIGA 2026)

## 1. Objective
Estruturar o modelo de monitoramento operacional e analítico da **Fase de Planejamento** das contratações públicas da Telebras no SIGA previstas para conclusão ainda no exercício de 2026.
O objetivo primordial é transformar a visão burocrática e estática do PLAC em uma **esteira Kanban dinâmica** orientada à ação, permitindo rastrear onde cada processo está, com quem está, o que está sendo produzido, quais os prazos decorridos e onde se concentram os gargalos críticos, evitando o represamento de demandas essenciais no final do ano.

---

## 2. Capability & Macro-Fases do Kanban

A esteira divide a fase preparatória de planejamento em 5 colunas sequenciais com regras claras de entrada e saída:

| Coluna | Macro-Fase | Responsável Típico | Peças/Documentos Esperados | SLA de Referência |
|---|---|---|---|---|
| **1** | **Autuação & DFD** | Área Demandante (Gerência Requisitante) | DOD / DFD formalizado no SIGA, Certidão de Alinhamento PLAC | 10 dias úteis |
| **2** | **ETP & Gestão de Riscos** | Equipe de Planejamento da Contratação | Estudo Técnico Preliminar (ETP), Matriz de Riscos Operacionais, RMS SAP | 35 dias úteis |
| **3** | **Pesquisa de Preços & TR/PB** | Demandante / Apoio Pesquisa GCC | Mapa Comparativo de Preços (IN 65/2021), Termo de Referência ou Projeto Básico | 20 dias úteis |
| **4** | **Análise Jurídica & Saneamento** | CONJUR / Área Técnica | Parecer Jurídico Consultivo, Notas Técnicas de Atendimento a Diligências | 15 dias úteis |
| **5** | **Triagem & Prontidão GCC** | GCC (Gerência de Compras e Contratos) | Checklist de Conformidade do Processo, Homologação no Calendário / Minuta de Edital | 10 dias úteis |

---

## 3. Esquema de Atributos do Processo no Kanban

Cada processo mapeado na esteira deve conter os seguintes metadados estruturados:

```json
{
  "numero_processo_siga": "TLB-PRO-2026/00XXXX",
  "ano_contratacao_previsto": 2026,
  "objeto": "Descrição detalhada do objeto da contratação",
  "unidade_demandante": "Código e Nome da Unidade (ex: 4200 - GTI)",
  "diretoria": "DAFRI / DTO / DGOV / PR",
  "origem_planejamento": "PLAC 2026 | PLAC 2025 | PLAC 2024 | PLAC 2023 | EXTRAORDINARIO",
  "codigo_item_plac": "Código de verificação do item no PLAC",
  "valor_estimado_rs": 0.00,
  "modelo_contratacao_previsto": "Pregão Eletrônico | Dispensa | Inexigibilidade",
  "amparo_legal": "Lei 13.303/2016 ou Lei 14.133/2021",
  "fase_kanban_id": "1_DFD | 2_ETP | 3_PESQUISA_TR | 4_JURIDICO | 5_GCC",
  "setor_atual_sigla": "Sigla da lotação atual no SIGA",
  "setor_atual_nome": "Nome por extenso do setor",
  "custodiante_atual": "Nome do servidor/analista com carga dos autos",
  "data_entrada_setor": "YYYY-MM-DD",
  "dias_no_setor_atual": 0,
  "dias_totais_tramitacao": 0,
  "status_prazo": "NO_PRAZO | ATENCAO | CRITICO_GARGALO",
  "acao_em_andamento": "Descrição do despacho ou trabalho em elaboração",
  "ultimo_despacho_resumo": "Texto resumido do último despacho no SIGA",
  "documentos_produzidos": [
    {"tipo": "DFD", "titulo": "...", "data": "...", "signatario": "...", "status": "JUNTADO"}
  ],
  "proximo_documento_pendente": "ETP / Pesquisa de Preços / Parecer Jurídico",
  "risco_prazo_2026": "ALTO | MEDIO | BAIXO"
}
```

---

## 4. Critérios de Cruzamento Multianual (PLAC 2023–2026)

1. **Prioridade 1 — Rastreio por Código Exato (`COD_VERIF`):**
   * Busca por códigos como `4200-GTI_01`, `3600-GINF_03`, `2400-GGP_05` no histórico textual ou despacho de autuação.
2. **Prioridade 2 — Rastreio por Número do Processo SIGA:**
   * Comparação do padrão `TLB-PRO-XXXX/XXXX` com os campos de processos cadastrados nas planilhas `Controle_Execucao_PLAC_GCC.xlsx` e anexos do PLAC.
3. **Prioridade 3 — Casamento Semântico e Objeto:**
   * Análise do objeto da contratação confrontando com as ementas das demandas planejadas nos PLACs de 2023, 2024, 2025 e 2026.
4. **Demandas Extraordinárias:**
   * Processos iniciados no SIGA que não possuam correspondência em nenhum dos PLACs vigentes são classificados formalmente como **"Não Previsto / Extraordinário"**, para auditoria da governança.

---

## 5. Estratégia de Verificação e Entregáveis

### 5.1. Entregável Fase 1 (Imediata)
* **Planilha Analítica em Excel (`BASE_PROCESSOS_PLANEJAMENTO_KANBAN_SIGA_2026.xlsx`):**
  - Aba 1: `PAINEL_KANBAN` (Visão tabular em colunas dos processos em trânsito no planejamento).
  - Aba 2: `INVENTARIO_GERAL` (Todos os processos mapeados com setor, custodiante, dias e valor).
  - Aba 3: `MATRIZ_GARGALOS` (Indicadores de tempo médio vs meta por setor demandante e interveniente).
  - Aba 4: `ARVORE_DOCUMENTOS` (Relação de peças produzidas vs pendentes por processo).
* **Relatório Executivo Oficial em PDF (`RELATORIO_EXECUTIVO_PLANEJAMENTO_KANBAN_SIGA_2026.pdf`):**
  - Formato paisagem A4, 3 páginas, cabeçalho Telebras, cartões de KPIs executivos, esteira colorida Kanban e tabela analítica de gargalos e diretrizes.

---

## 6. Boundaries (Limites de Execução)

* **Always:**
  - Extrair ou consolidar todos os processos reais ou vigentes de 2026 que tramitam na fase preparatória.
  - Explicitar o tempo em dias úteis e corridos de cada processo no setor atual.
  - Identificar os responsáveis e as pendências documentais.
* **Ask First:**
  - Iniciar qualquer edição de arquivos `.py` no backend Django ou `.jsx` no frontend React.
  - Alterar modelos de banco de dados ou migrações do PostgreSQL.
* **Never:**
  - Alterar o código da aplicação antes da entrega e validação dos relatórios em PDF e Excel.
  - Inventar processos inexistentes sem indicar explicitamente a sua fonte ou status no SIGA.

---

## 7. Success Criteria

1. A planilha Excel conter 100% dos processos identificados de 2026 na fase de planejamento com suas respectivas colunas do Kanban, prazos e documentos.
2. O relatório em PDF conter exatamente 3 páginas horizontais no padrão corporativo da Telebras, sem corte de texto ou transbordamento.
3. Apresentação ao gestor dos maiores pontos de estrangulamento identificados na esteira preparatória.
