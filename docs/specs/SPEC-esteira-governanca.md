# Spec: Módulo esteira-governanca (Esteira de Governança do Planejamento PLAC)

## Objective
Implementar a **Esteira Visual de Governança do Planejamento PLAC** estruturada nas 5 fases oficiais do ciclo de planejamento de contratações da Telebras, com filtragem dinâmica por quadrimestre (Q1, Q2, Q3), trava de governança inviolável na aprovação da Diretoria (verificação prévia de amarração do processo SIGA com a Certidão do PLAC), semáforo em tempo real de capacidade da GCC e emissão da Minuta Consolidada do PLAC em PDF para deliberação da REDIR.

### Fases da Esteira de Governança (Funil PLAC)
1. **1. Levantamento de Necessidades (`AGUARDANDO_VALIDACAO`):**
   - Registrado pela área demandante (Blocos 1 a 5).
   - Demanda possui Código de Rastreio gerado (`PLAC-[ANO]-[ÁREA]+[NÚMERO]`).
   - Demanda exibe indicador de status da Certidão e se já foi autuado e vinculado o processo no SIGA (`TLB-PRO-XXXX/XXXXX`).
2. **2. Validação pela Diretoria (`VALIDADO_DIRETOR`):**
   - **Trava de Ouro da Governança:** O Diretor só pode aprovar estrategicamente se a demanda tiver o Código de Rastreio gerado E o número do processo SIGA devidamente vinculado.
   - Tentativas de aprovação sem processo SIGA vinculado são bloqueadas pelo backend com HTTP 400 e sinalizadas no frontend com alerta instrutivo: *"Aprovação Bloqueada: A área demandante deve autuar o processo no SIGA com a Certidão do PLAC como Peça nº 01 e vincular o número TLB-PRO antes do julgamento estratégico."*
   - O Diretor pode também devolver a demanda para ajustes (`DEVOLVIDO_AJUSTES`) informando o motivo.
3. **3. Consolidação GCC & SLA (`CONSOLIDADO`):**
   - A GCC recebe as demandas validadas pela Diretoria com processo SIGA em curso.
   - Enquadramento em uma das 10 modalidades de contratação com cálculo de SLA e data-limite de envio.
   - Detecção de sobrecarga de capacidade da GCC no quadrimestre pretendido e marcação de urgência fabricada.
   - Exportação da **Minuta Consolidada do PLAC em PDF** para instrução do processo de deliberação.
4. **4. Deliberação REDIR & Parecer DAFRI (`DELIBERACAO_REDIR` / `APROVADO_REDIR`):**
   - Parecer técnico da DAFRI e aprovação colegiada da Diretoria Executiva (Ata REDIR).
5. **5. Calendário de Contratações Vigentes (`VIGENTE` / `CONTRATADO`):**
   - Inclusão oficial da demanda no Calendário Anual de Contratações da Telebras para execução pela GCC e áreas técnicas.

---

## Filtros e Semáforos por Quadrimestre
- Segmentação por Quadrimestres Telebras:
  - **Todos**
  - **Q1 (Jan–Abr)**: Apuração em 30/04
  - **Q2 (Mai–Ago)**: Apuração em 31/08
  - **Q3 (Set–Dez)**: Apuração em 31/12
- Painel de Carga no Topo da Esteira:
  - Total de Demandas e Valor Orçamentário Total no período.
  - Indicador de Capacidade da GCC (Verde < 6 processos, Amarelo 6–8 processos, Vermelho > 8 processos simultâneos).
  - Alerta de "Urgências Fabricadas" com data fatal de abertura no SIGA já vencida.

---

## Tech Stack & Commands
- **Backend:** Python 3.11, Django 5.0, DRF, ReportLab 5.0.
- **Frontend:** React 18, Vite, Tailwind CSS.

### Comandos de Verificação
- Backend Tests: `docker exec plac-mvp-backend-1 python manage.py test demands.test_governanca --no-input`
- Full Demands Tests: `docker exec plac-mvp-backend-1 python manage.py test demands --no-input`
- Frontend Build: `docker exec plac-mvp-frontend-1 npm run build`

---

## Boundaries
- **Always:** Bloquear aprovação do Diretor se `siga_process_number` estiver em branco ou nulo.
- **Always:** Recalcular os totais de demandas, orçamento e semáforo da GCC ao trocar o filtro de quadrimestre.
- **Never:** Permitir avanço manual para fase posterior sem passar pelas validações regimentais.
- **Never:** Permitir perda do Código de Rastreio ou processo SIGA nas movimentações de fase.

---

## Success Criteria
1. Teste automatizado confirma que `approve` retorna erro HTTP 400 se a demanda não possuir `siga_process_number`.
2. Teste automatizado confirma que com `siga_process_number` preenchido a aprovação tem sucesso e avança para `VALIDADO_DIRETOR`.
3. Endpoint de Minuta Consolidada gera PDF válido contendo a relação de demandas aprovadas com seus respectivos códigos de rastreio e números SIGA.
4. Componente React `PlanejamentoEsteiraKanban.jsx` renderiza as colunas da esteira, permite alternar filtros Q1/Q2/Q3 e interagir com as ações de cada fase.
5. Build de produção do Vite compila sem erros.
