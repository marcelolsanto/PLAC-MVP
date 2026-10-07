# SPEC-008: Auditoria de Adesão das Contratações ao PLAC via SIGA

## 1. Objetivo
Desenvolver uma esteira de auditoria automatizada que cruze os contratos formalizados da Telebras (planilha `15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx`, aba `BASE CTR FINALIZADOS`) com o planejamento do PLAC 2026 (planilha `ANEXOS_PLAC 2026 1.xlsx`, aba `BASE_PLAC_2026`), inspecionando os autos, volumes e peças dos processos no SIGA (`https://intranet2.telebras.com.br/sigaex`) para rastrear o uso do Código Verificador (`COD VERIF`) do ciclo de 2024 a 2026 e a conformidade do objeto contratado, gerando:
1. Uma base de dados estruturada em Excel e JSON;
2. Um Relatório Executivo em PDF de alta qualidade para apresentação à Diretoria Executiva e áreas demandantes.

---

## 2. Fontes de Dados e Mapeamento

### 2.1. Planilha 15 (`15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx`)
- **Aba:** `BASE CTR FINALIZADOS`
- **Campos Chave:**
  - Coluna G (index 6): `Nº PROCESSO SIGA` (`TLB-PRO-XXXX/XXXXX` ou `53000...`)
  - Coluna O (index 14): `Nº CONTRATO` (`TLB-CTR-...`, `2024NE...`, etc.)
  - Coluna C (index 2): `Data inicio processo`
  - Coluna E (index 4): `DIRETORIA`
  - Coluna F (index 5): `ÁREA REQUISITANTE`
  - Coluna H (index 7): `MODALIDADE`
  - Coluna T (index 19): `MÊS ASSINATURA`
  - Coluna U (index 20): `INÍCIO VIGÊNCIA` (Data de Formalização / Vigência)
  - Coluna X (index 23): `OBJETO`
  - Coluna Z (index 25): `FORNECEDOR`
  - Coluna AD (index 29): `VALOR CONTRATO`

### 2.2. Planilha PLAC 2026 (`ANEXOS_PLAC 2026 1.xlsx`)
- **Aba:** `BASE_PLAC_2026`
- **Campos Chave (Cabeçalho na Linha 4):**
  - Coluna B (index 1): `COD VERIF` (ex: `1100-GAB PR_01`, `2200-GLOG_05`, etc.)
  - Coluna D (index 3): `Gerência`
  - Coluna E (index 4): `Diretoria`
  - Coluna I (index 8): `Objeto`
  - Coluna K (index 10): `Data prevista da contratação`
  - Coluna M (index 12): `Valor estimado 2026`

### 2.3. Sistema SIGA (Intranet Telebras)
- **Autenticação:** POST em `https://intranet2.telebras.com.br/siga/public/app/login` com usuário corporativo e senha.
- **Pesquisa de Processos:** Consulta de expedientes por número de processo em `/sigaex/app/expediente/doc/listar` ou `/sigaex/app/expediente/doc/exibir`.
- **Inspeção de Autos e Volumes:** Leitura do extrato de documentos (DFD, ETP, TR, Certidão de Aderência ao PLAC, Pareceres Jurídicos e Contratos) buscando citações a `COD VERIF` e termos do objeto.

---

## 3. Matriz de Classificação de Adesão ao PLAC

| Categoria | Descrição | Regra de Inferência |
|---|---|---|
| **PREVISTA (COM COD VERIF)** | Contratação 100% regular com rito cumprido | `COD VERIF` (2024-2026) localizado nos autos do SIGA ou registrado na coluna do processo. |
| **PREVISTA (VINCULADA POR OBJETO)** | Contratação planejada no PLAC, mas com falha no rito operacional do SIGA | Sem `COD VERIF` nos autos, mas Objeto + Área demandante possuem correspondência comprovada no `BASE_PLAC_2026`. |
| **NÃO PREVISTA (EXTRAORDINÁRIA)** | Contratação não constante no planejamento do PLAC | Nenhum código ou objeto correspondente identificado no planejamento. |

---

## 4. Entregáveis e Estrutura de Arquivos

1. **Crawler & Auditor do SIGA:** `services_auditoria_plac_siga.py`
2. **Dataset Consolidado:** `Z:\PLAC-MVP\AUDITORIA_ADESAO_PLAC_2026_SIGA.xlsx` e `.json`
3. **Relatório Executivo PDF:** `Z:\PLAC-MVP\RELATORIO_EXECUTIVO_AUDITORIA_ADESAO_PLAC_SIGA.pdf`

---

## 5. Critérios de Aceite
- [x] Sessão autenticada no SIGA estabelecida com sucesso usando credenciais corporativas.
- [x] Todos os contratos com número de processo na planilha 15 processados.
- [x] Rastreamento exaustivo de `COD VERIF` e similaridade semântica de objeto.
- [x] Relatório em PDF gerado contendo Processo, Data de Formalização, Valor, Status, Código e Métricas por Diretoria.
