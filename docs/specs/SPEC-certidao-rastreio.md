# Spec: Módulo certidao-rastreio (Certidão Oficial & Código de Rastreio PLAC)

## Objective
Padronizar e automatizar a emissão da **Certidão Oficial de Planejamento e Conformidade PLAC** e o respectivo **Código de Rastreio de Gestão** (`PLAC-[ANO]-[ÁREA]+[NÚMERO]`), viabilizando a amarração formal do planejamento com o processo administrativo autuado no SIGA (`TLB-PRO-XXXX/XXXXX`).

### Responsabilidades Centrais
1. **Geração do Código de Rastreio Único:**
   - Formato normatizado: `PLAC-[ANO]-[SIGLA_DIRETORIA]+[SEQUENCIAL_4_DIGITOS]`.
   - Exemplo: `PLAC-2026-DTO+0042`, `PLAC-2026-GCC+0001`.
2. **Emissão da Certidão em PDF Institucional (ReportLab):**
   - Cabeçalho oficial Telebras.
   - Dados completos da Demanda (Objeto, Valor, Diretoria, Gerência, Responsável).
   - Enquadramento em uma das 10 modalidades da GCC com SLA em dias úteis.
   - Cronograma Reverso Obrigatório (Data Fatal Abertura SIGA, Data Limite GCC, Assinatura, Quadrimestre-Alvo).
   - Instrução ao Protocolo/SIGA: Esta certidão é a Peça nº 01 do processo administrativo.
   - Carimbo de Validação do Diretor e Hash SHA-256 de Autenticidade Documental.
3. **Mecanismo de Amarração com o SIGA (Process Binding):**
   - Endpoint e interface para registrar o número do processo gerado no SIGA (`TLB-PRO-XXXX/XXXXX`), estabelecendo a ponte entre a Demanda no PLAC e os Robôs de Monitoramento.

## Tech Stack & Commands
- **Backend:** Python 3.11, Django 5.0, DRF, ReportLab 5.0.
- **Frontend:** React 18, Vite, Tailwind CSS.

### Comandos de Verificação
- Backend Tests: `docker exec plac-mvp-backend-1 python manage.py test demands.test_certidao --no-input`
- Full Demands Tests: `docker exec plac-mvp-backend-1 python manage.py test demands --no-input`
- Frontend Build: `docker exec plac-mvp-frontend-1 npm run build`

## Project Structure
- `backend/demands/services_certidao.py` -> Gerador de código de rastreio, cálculo de hash SHA-256 e renderização do PDF com ReportLab.
- `backend/demands/test_certidao.py` -> Testes unitários de geração de código, integridade do PDF e binding com o SIGA.
- `backend/demands/views.py` -> Views `EmitirCertidaoPdfView`, `VincularProcessoSigaView`, `CertidaoDadosView`.
- `backend/demands/urls.py` -> Registro das novas rotas de certidão e amarração.
- `frontend/src/components/CertidaoVinculacaoModal.jsx` -> Modal no frontend para visualização prévia da certidão, download do PDF e formulário de amarração do `TLB-PRO`.

## Boundaries
- **Always:** O código de rastreio deve ser imutável após a emissão da certidão; o hash SHA-256 deve cobrir os campos essenciais da demanda (ID, código, valor, data, objeto).
- **Never:** Permitir duplicidade de código de rastreio ou vinculação de processo com formato inválido.

## Success Criteria
- Testes automatizados cobrindo geração de PDF em memória, códigos de rastreio e binding aprovados com 100%.
- Download de PDF retornando Content-Type `application/pdf` e renderizando corretamente no leitor PDF.
- Frontend permitindo ao usuário visualizar e vincular o `TLB-PRO` em tempo real.
