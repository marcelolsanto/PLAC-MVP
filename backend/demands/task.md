# Tarefas de Remoção de Mocks e Adoção de Banco de Dados

- [x] **Remover caches JSON**
  - [x] Deletar siga_cache_139_procs.json
  - [x] Deletar AUDITORIA_CONTRATOS_VIGENTES_2026_SIGA.json
  - [x] Remover referencias a caches locais em JSON.

- [x] **Atualizar services_kanban_planejamento.py**
  - [x] Remover dependência de openpyxl e ANEXOS_PLAC 2026 1.xlsx.
  - [x] Modificar _carregar_base_bruta() para buscar no modelo Demand (conectado ao SIGA).

- [x] **Atualizar services_contratos_fluxo.py**
  - [x] Remover leitura de 15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx.
  - [x] Refatorar para buscar no modelo Contract ou PncpContract.

- [x] **Atualizar services_auditoria_plac_siga.py**
  - [x] Remover ANEXOS_PLAC 2026 1.xlsx e outputs mockados.
  - [x] Refatorar para cruzar as models Demand e SigaProcess reais.

- [x] **Atualizar services_stats.py**
  - [x] Substituir arrays empíricos por cálculos em tempo real de SigaEvent.

- [x] **Verificação Final**
  - [x] Rodar git grep openpyxl backend/ e garantir 0 resultados em queries do sistema.
  - [x] Testes rodando com as bases de dados e evitando o uso de mock.
