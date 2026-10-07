# Declaração de Intenção: Auditoria de Adesão das Contratações ao PLAC via SIGA

- **Resultado (Outcome):** Base de dados consolidada (Excel/JSON) e Relatório Executivo em PDF auditando a adesão ao PLAC dos contratos formalizados (planilha 15. CONTRATOS_ARP_finalizados_PNCP e SITE.xlsx, aba BASE CTR FINALIZADOS, colunas G [Processos] e O [Contratos]), rastreando códigos verificadores (COD VERIF) do ciclo **2024 a 2026** nos autos e volumes do SIGA (TB53137) e cruzando o objeto na aba BASE_PLAC_2026 (coluna I), classificando cada contratação em:
  1. **Prevista (com COD VERIF comprovado no SIGA)**;
  2. **Prevista (por correspondência de Objeto no PLAC, apontando falha de rito operacional no SIGA)**;
  3. **Não Prevista (Extraordinária / sem lastro no PLAC)**.
- **Usuário/Beneficiário:** Gerência de Contratações (GCC), Governança e Diretorias da Telebras para prestação de contas, apresentação da maturidade de planejamento das áreas demandantes e cobrança de governança.
- **Por que agora:** Avaliar a conformidade real da execução contratual frente ao planejamento do PLAC (2024 a 2026), evidenciando quais áreas cumprem o rito de registro do código no SIGA e quais demandam fora do planejado.
- **Critério de Sucesso:** Processos de contratos da planilha 15 auditados via SIGA; rastreamento do COD VERIF (2024-2026) e correspondência de objeto; geração de base estruturada e emissão do PDF executivo contendo Número do Processo, Data de Formalização, Valor do Contrato, Status no PLAC, Código Verificador vinculado e métricas/gráficos de adesão por Diretoria e Gerência.
- **Restrição vinculante:** O robô autentica no SIGA (TB53137 / #Mr321456), inspeciona processos (TLB-PRO-...), volumes e peças documentais (DFD, ETP, TR, Certidão PLAC) buscando referências a COD VERIF (2024-2026) e termos do Objeto.
- **Fora de escopo:** Acesso estritamente de leitura/auditoria no SIGA (sem gravar despachos ou alterar peças); contratações anteriores a 2024 fora da planilha 15 não serão contempladas.
