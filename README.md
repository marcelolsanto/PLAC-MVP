# Sistema de Gestão do PLAC - MVP

Protótipo executável do Sistema de Gestão do Plano Anual de Contratações (PLAC) construído de ponta a ponta com **Django REST Framework (Python)**, **PostgreSQL** e **React (Vite + Tailwind CSS)**.

---

## 🚀 Como Executar com Docker

Clone ou copie o repositório para o seu servidor e execute:

```bash
docker-compose up --build
```

### 🌐 Endereços das Aplicações:
- **Frontend (Interface Web):** [http://localhost:3030](http://localhost:3030)
- **Backend API (Django REST):** [http://localhost:8085/api/](http://localhost:8085/api/)
- **Banco de Dados (PostgreSQL):** porta `5444`

---

## 👥 Usuários de Teste Pré-Configurados
O contêiner do backend cria automaticamente os seguintes usuários para testes:

| Usuário | Perfil | Senha Padrão |
|---|---|---|
| `demandante` | Representante da Área Demandante (UC01) | `password123` |
| `diretor` | Diretor(a) da Área Requisitante (UC02) | `password123` |
| `analista_gcc` | Analista da GCC (UC03) | `password123` |
| `diretoria_executiva` | Diretoria Executiva (UC04) | `password123` |

---

## 🔄 Fluxos de Demonstração

1. **UC01 - Registro e Priorização:** Faça login ou use a aba *Registrar Necessidades*, preencha os dados e notas de F1 a F4. O motor calcula a prioridade automaticamente.
2. **UC02 - Validação do Diretor:** Na aba *Painel do Diretor*, valide a demanda ou devolva para ajustes com comentário obrigatório.
3. **UC03 - Consolidação GCC & Calendário:** Na aba *Consolidação GCC*, selecione a forma de contratação (ex: Pregão com SLA de 157 dias) e veja o cálculo automático da data-limite e alerta visual de antecipação.
4. **UC04 - Painel Executivo:** Na aba *Painel Executivo*, acompanhe os indicadores TEP e IAC e clique no botão para simular a sincronização com o PNCP e sistemas legados.

---

## ⚙️ CI/CD (GitHub Actions)
O pipeline em `.github/workflows/ci.yml` executa automaticamente a cada push:
- Testes unitários do motor de priorização em Python 3.11.
- Build do frontend React.
- Validação estrutural do Docker Compose.
