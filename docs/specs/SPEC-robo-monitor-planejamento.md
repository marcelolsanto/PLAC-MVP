# Spec: Módulo robo-monitor-planejamento (Sentinela de Conformidade e Telemetria PLAC)

## Objective
Implementar o **Robô Sentinela de Planejamento e Conformidade do PLAC**, fornecendo motor autônomo de auditoria, apuração dos 4 indicadores oficiais de desempenho da Telebras (**IAC**, **ICNP**, **TEP**, **TMP**) e fiscalização analítica das áreas demandantes para erradicar "urgências fabricadas", inércia processual e desvio de responsabilidade contra a GCC.

### Responsabilidades Centrais
1. **Apuração dos 4 Indicadores Oficiais de Desempenho:**
   - **IAC (Índice de Aderência ao Calendário):** Percentual de demandas cumpridas no prazo sem antecipação forçada ou dilação. Meta Telebras: >= 85%.
   - **ICNP (Índice de Contratações Não Planejadas):** Percentual de demandas extraordinárias ou urgências fabricadas fora do rito anual. Meta Telebras: <= 10%.
   - **TEP (Taxa de Execução do Plano):** Percentual de demandas efetivamente contratadas e publicadas em relação ao total planejado.
   - **TMP (Tempo Médio de Planejamento):** Decomposição em dias do tempo decorrido na Área Demandante (ETP/TR) versus tempo na GCC (processamento do certame), desmistificando o gargalo burocrático.
2. **Matriz e Ranking de Conformidade por Área Requisitante:**
   - Avaliação por Diretoria (DTO, DAFRI, DSI, etc.) e Gerência (GTI, GLOG, GROP, etc.):
     - Total de demandas cadastradas e volume orçamentário.
     - Taxa de cumprimento do rito do PLAC.
     - Quantidade de urgências fabricadas e processos abertos fora do prazo fatal.
     - Taxa de amarração com o processo SIGA (Peça nº 01).
     - Score de Governança da Área (0 a 100) e Classificação (Exemplar, Moderado, Crítico/Prolixo).
3. **Motor de Varredura e Alertas em Tempo Real (Sentinela Autônomo):**
   - Varredura de inconsistências no banco de dados do PLAC e no espelho do SIGA:
     - Demandas cuja data fatal de abertura no SIGA já expirou sem processo vinculado.
     - Demandas cujo SLA regimental da modalidade (ex: 144 dias para Pregão) excede o tempo até a data pretendida.
     - Processos SIGA sem referência explícita ao Código de Rastreio (`PLAC-[ANO]-[ÁREA]+[NUM]`).
4. **Relatório Analítico de Fiscalização:**
   - Emissão de dossiê consolidado de conformidade para a Diretoria Executiva (REDIR) e Auditoria Interna.

---

## Tech Stack & Commands
- **Backend:** Python 3.11, Django 5.0, DRF.
- **Frontend:** React 18, Vite, Tailwind CSS, Recharts / SVG gauges.

### Comandos de Verificação
- Backend Tests: `docker exec plac-mvp-backend-1 python manage.py test demands.test_monitor_planejamento --no-input`
- Full Demands Tests: `docker exec plac-mvp-backend-1 python manage.py test demands --no-input`
- Frontend Build: `docker exec plac-mvp-frontend-1 npm run build`

---

## Project Structure
- `backend/demands/services_monitor.py` -> Motor de cálculo dos 4 KPIs, ranking de áreas demandantes e rotina de varredura do sentinela.
- `backend/demands/test_monitor_planejamento.py` -> Testes unitários para IAC, ICNP, TEP, TMP, ranking de conformidade e detecção de urgências fabricadas.
- `backend/demands/views.py` -> Endpoints `SentinelaMetricasView`, `SentinelaRankingAreasView`, `SentinelaVarreduraView`.
- `backend/demands/urls.py` -> Registro das rotas do sentinela.
- `frontend/src/components/PlanejamentoSentinelaMonitor.jsx` -> Painel executivo do Sentinela com velocímetros dos 4 KPIs, ranking das áreas demandantes e feed de alertas de inércia.
- `frontend/src/pages/Dashboard.jsx` & `ContratosFluxoModule.jsx` -> Exposição do Sentinela de Planejamento.

---

## Boundaries
- **Always:** O cálculo do IAC deve penalizar toda demanda com `needs_anticipation=True` ou cuja abertura no SIGA ocorreu após a data fatal.
- **Always:** A decomposição do TMP deve mensurar separadamente os dias de responsabilidade da Área Demandante e os dias da GCC.
- **Never:** Permitir mascarar o ICNP como contratação planejada sem que haja registro na esteira do PLAC.

---

## Success Criteria
1. Teste automatizado confirma apuração matemática precisa de IAC, ICNP, TEP e TMP com cenários sintéticos e reais.
2. Teste automatizado valida a geração do ranking de conformidade com penalização de áreas com urgências fabricadas.
3. Varredura do sentinela identifica corretamente demandas em atraso fatal e sem processo SIGA.
4. Componente React `PlanejamentoSentinelaMonitor.jsx` renderiza os indicadores, ranking e feed de alertas.
5. Suíte completa de testes de `demands` e build do frontend continuam 100% aprovados.
