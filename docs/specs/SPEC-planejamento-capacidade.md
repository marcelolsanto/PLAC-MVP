# Spec: Módulo planejamento-capacidade (Robô de Gestão de Planejamento)

## Objective
Fornecer os serviços de inteligência matemática do **Robô de Gestão de Planejamento**, atuando no momento do cadastro da necessidade pelo Diretor/Área Demandante para:
1. **Calcular o Cronograma Reverso (Backward Scheduling):** A partir da data pretendida de homologação/assinatura e da modalidade (entre as 10 da GCC), calcular em dias úteis a data-limite fatal de envio do ETP à GCC e a data necessária de autuação do processo no SIGA.
2. **Verificar a Capacidade Operacional da GCC:** Analisar a esteira contínua do Calendário de Contratações e apurar se o acréscimo da nova demanda gera sobrecarga simultânea na equipe da GCC (teto padrão de 8 certames concorrentes de alta complexidade).
3. **Recomendar Janelas Cabíveis / Slots Livres:** Caso a data solicitada cause sobrecarga ou viole o SLA mínimo da modalidade, sugerir de forma autônoma as próximas datas e quadrimestres viáveis no calendário para distribuição equilibrada das compras.

## Tech Stack & Commands
- **Backend:** Python 3.11, Django 4.2+, Django REST Framework.
- **Frontend:** React 18, Vite, Tailwind CSS, Lucide Icons.
- **Banco de Dados:** PostgreSQL (modelo \Demand\).

### Comandos de Verificação
- Backend Tests: \docker exec plac-mvp-backend-1 python manage.py test demands.test_capacidade --no-input- Frontend Build: \docker exec plac-mvp-frontend-1 npm run build- Linting: \docker exec plac-mvp-frontend-1 npm run lint
## Project Structure
- \ackend/demands/services_capacidade.py\ -> Motor algorítmico de dias úteis, cálculo reverso, mapa de capacidade e alocação de slots.
- \ackend/demands/views.py\ -> ViewSets e endpoints da API de capacidade.
- \ackend/demands/urls.py\ -> Rotas \/api/planejamento/verificar-capacidade/\, \/api/planejamento/cronograma-reverso/\, \/api/planejamento/janelas-disponiveis/\.
- \ackend/demands/test_capacidade.py\ -> Bateria de testes unitários do motor de capacidade e agendamento.
- \rontend/src/components/PlanejamentoCapacidadeWidget.jsx\ -> Widget integrado ao cadastro de necessidade exibindo o semáforo de capacidade, data fatal no SIGA e seletor de janelas sugeridas.

## Code Style & Algorithms

### 1. Algoritmo de Cronograma Reverso
Dado o prazo $ em dias úteis da modalidade selecionada (ex: 144 dias úteis para Pregão):
\\[ \text{Data-Limite Envio GCC} = \text{Data Pretendida} - SLA_{\text{modalidade}} \text{ (dias úteis)} \\]
\\[ \text{Data Fatal Abertura SIGA} = \text{Data-Limite Envio GCC} - 15 \text{ dias úteis (elaboração do ETP)} \\]

### 2. Semáforo de Capacidade Operacional
- \textbf{VERDE (Disponível):} Menos de 6 certames ativos na mesma janela quadrimestral/mês.
- \textbf{AMARELO (Atenção / Pré-Lotação):} Entre 6 e 8 certames ativos.
- \textbf{VERMELHO (Sobrecarga / Incompatível):} Mais de 8 certames ativos OU data de envio resultante no passado.

## Testing Strategy
- Teste unitário de cálculo reverso para todas as 10 modalidades com feriados nacionais.
- Teste de saturação de carga simulando o Calendário com 8 certames no mesmo mês.
- Teste de proposição automática da próxima janela cabível (slot subsequente).
- Teste de integração via API REST com validação de payload JSON.

## Boundaries
- **Always:** Descontar feriados e fins de semana; validar existência da modalidade no catálogo oficial da GCC.
- **Ask first:** Alterar a capacidade máxima padrão da GCC (8 certames simultâneos).
- **Never:** Permitir validação com data fatal retroativa (no passado) sem gerar a flag explícita de URGÊNCIA FABRICADA / NÃO PLANEJADA.

## Success Criteria
- Testes automatizados executados no servidor com 100% de sucesso.
- Endpoint de verificação de capacidade respondendo em < 50ms.
- Componente frontend exibindo feedback imediato e visual amigável para o Diretor/Demandante.
