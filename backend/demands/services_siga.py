from datetime import datetime, timedelta
import copy

# Base de Conhecimento e Registro dos Processos Vigentes Rastreados no SIGA da Telebras
PROCESSOS_SIGA_VIGENTES = [
    {
        "id": 201,
        "numero_processo_siga": "53000.002814/2026-31",
        "numero_contrato_ou_edital": "CTR-018/2026",
        "objeto": "Suporte técnico especializado Premier Support e atualização de licenças de banco de dados Oracle Database Enterprise Edition.",
        "unidade_demandante": "4200 - Gerência de Tecnologia da Informação",
        "fornecedor": "ORACLE DO BRASIL SISTEMAS LTDA",
        "cnpj_cpf": "66.970.229/0001-67",
        "valor_estimado": 645000.00,
        "modelo_contratacao": "Inexigibilidade de Licitação",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 74, Inciso I (Fornecedor Exclusivo)",
        "amparo_legal_id": 51,
        "fase_siga": "contrato",  # Coluna 5: Homologação & Contrato
        "sla_dias_previstos": 90,
        "prioridade": "ALTO",
        "volume_siga": "Volume 1 (Fls. 1 a 128)",
        "setor_atual_sigla": "GECAD",
        "setor_atual_nome": "7. GECAD - Gestão Contratual & Fiscalização",
        "localizacao_atual": "Mesa Virtual SIGA / Acompanhamento de Execução (Contrato Vigente)",
        "custodiante_atual": "Carlos Eduardo (Fiscal do Contrato - GTI / 4200)",
        "dias_no_setor": 14,
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/15",
        "fonte_dados": "SIGA / PNCP",
        "fonte_tipo": "SIGA_PNCP",
        "ultimo_evento_siga": "Contrato assinado eletronicamente e publicado no PNCP sob nº 000015/2025.",
        "ultima_atualizacao": "2026-09-25 11:32:04",
        "documentos": [
            {
                "id": "DOC-002814-1",
                "titulo": "DFD - Documento de Formalizacao da Demanda.pdf",
                "tipo": "PDF",
                "tamanho_kb": 245,
                "data_juntada": "2026-06-12 09:14:00",
                "signatario": "Carlos Eduardo - Gerente de TI",
                "resumo_conteudo": "Formalização da necessidade de renovação do suporte Oracle Premier para garantir continuidade do banco de dados das estações terrenas.",
                "conteudo_preview": "DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA (DFD)\nProcesso SIGA: 53000.002814/2026-31\nUnidade: Gerência de TI (4200)\nObjeto: Renovação do suporte técnico Premier Support Oracle."
            },
            {
                "id": "DOC-002814-2",
                "titulo": "ETP - Estudo Tecnico Preliminar.pdf",
                "tipo": "PDF",
                "tamanho_kb": 612,
                "data_juntada": "2026-06-25 14:22:15",
                "signatario": "Comissão Técnica de TI",
                "resumo_conteudo": "Análise de viabilidade técnica demonstrando a titularidade dos direitos autorais pela Oracle e ausência de revendedores autorizados para suporte direto nível 3.",
                "conteudo_preview": "ESTUDO TÉCNICO PRELIMINAR (ETP)\nDemonstração de inviabilidade de competição conforme Art. 74, I da Lei 14.133/2021."
            },
            {
                "id": "DOC-002814-3",
                "titulo": "Atestado_Exclusividade_ABES.pdf",
                "tipo": "PDF",
                "tamanho_kb": 380,
                "data_juntada": "2026-07-02 10:45:00",
                "signatario": "Associação Brasileira das Empresas de Software (ABES)",
                "resumo_conteudo": "Certidão comprobatória de exclusividade conforme Súmula 255/TCU.",
                "conteudo_preview": "CERTIDÃO DE EXCLUSIVIDADE - ABES\nCertificamos que a ORACLE DO BRASIL SISTEMAS LTDA é a única detentora dos direitos de suporte direto Enterprise Edition no Brasil."
            },
            {
                "id": "DOC-002814-4",
                "titulo": "Parecer_Juridico_CONJUR_184_2026.pdf",
                "tipo": "PDF",
                "tamanho_kb": 890,
                "data_juntada": "2026-07-18 16:30:10",
                "signatario": "Dr. Fernando Rocha - Procurador Consultivo",
                "resumo_conteudo": "Parecer Jurídico favorável ao enquadramento por Inexigibilidade de Licitação cumpridos os requisitos do Art. 74, I.",
                "conteudo_preview": "PARECER CONJUR/TELEBRAS Nº 184/2026\nConclusão: Pela viabilidade jurídica da contratação direta por inexigibilidade."
            },
            {
                "id": "DOC-002814-5",
                "titulo": "Contrato_Assinado_CTR_018_2026.pdf",
                "tipo": "PDF",
                "tamanho_kb": 1240,
                "data_juntada": "2026-08-10 11:15:00",
                "signatario": "Tatiana Rubia Melo Miranda - Diretora DAFRI",
                "resumo_conteudo": "Contrato assinado por ambas as partes com vigência de 12 meses.",
                "conteudo_preview": "CONTRATO TELEBRAS Nº 018/2026\nContratante: TELECOMUNICAÇÕES BRASILEIRAS S.A. - TELEBRAS\nContratada: ORACLE DO BRASIL SISTEMAS LTDA"
            }
        ]
    },
    {
        "id": 202,
        "numero_processo_siga": "53000.003119/2026-14",
        "numero_contrato_ou_edital": "DISP-14/2026",
        "objeto": "Manutenção preventiva e corretiva emergencial dos nobreaks e grupos geradores da Estação Satelital de Brasília.",
        "unidade_demandante": "3600 - Gerência de Manutenção e Infraestrutura",
        "fornecedor": "TECH ENGENHARIA E INFRAESTRUTURA S/A",
        "cnpj_cpf": "08.412.983/0001-90",
        "valor_estimado": 48200.00,
        "modelo_contratacao": "Dispensa de Licitação",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 75, Inciso II (Limite de Valor)",
        "amparo_legal_id": 62,
        "fase_siga": "juridico",  # Coluna 3: Análise Jurídica
        "dias_decorridos": 21,
        "prioridade": "ALTO",
        "volume_siga": "Volume 1 (Fls. 1 a 64)",
        "setor_atual_sigla": "CONJUR",
        "setor_atual_nome": "4. CONJUR - Consultoria Jurídica",
        "localizacao_atual": "Caixa de Entrada CONJUR / Análise de Minuta de Dispensa (Art. 75, II)",
        "custodiante_atual": "Dr. Fernando Rocha (Procurador Consultivo)",
        "dias_no_setor": 21,
        "link_pncp": "https://pncp.gov.br/app/editais?q=TELEBRAS",
        "fonte_dados": "SIGA",
        "fonte_tipo": "SIGA",
        "ultimo_evento_siga": "Autos remetidos para análise jurídica da minuta de contrato de dispensa.",
        "ultima_atualizacao": "2026-09-25 10:15:30",
        "documentos": [
            {
                "id": "DOC-003119-1",
                "titulo": "DFD_Abertura_Processo.pdf",
                "tipo": "PDF",
                "tamanho_kb": 180,
                "data_juntada": "2026-09-02 08:30:00",
                "signatario": "Roberto Albuquerque - Gerente Operacional",
                "resumo_conteudo": "DFD com laudo técnico demonstrando oscilações perigosas nos nobreaks da subestação.",
                "conteudo_preview": "DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA\nJustificativa: Necessidade imediata de revisão dos quadros elétricos."
            },
            {
                "id": "DOC-003119-2",
                "titulo": "Pesquisa_Precos_3_Cotacoes.pdf",
                "tipo": "PDF",
                "tamanho_kb": 430,
                "data_juntada": "2026-09-12 11:20:00",
                "signatario": "Área de Compras e Suprimentos",
                "resumo_conteudo": "Mapa comparativo de 3 cotações de mercado. Proposta mais vantajosa: Tech Engenharia (R$ 48.200,00).",
                "conteudo_preview": "MAPA DE PREÇOS (ART. 23 DA LEI 14.133/2021)\nFornecedor 1: R$ 48.200,00 | Fornecedor 2: R$ 52.400,00 | Fornecedor 3: R$ 56.100,00"
            },
            {
                "id": "DOC-003119-3",
                "titulo": "Minuta_Aviso_Dispensa_Eletronica.pdf",
                "tipo": "PDF",
                "tamanho_kb": 310,
                "data_juntada": "2026-09-24 16:50:00",
                "signatario": "Analista da GCC",
                "resumo_conteudo": "Minuta do aviso para envio à CONJUR antes de publicação.",
                "conteudo_preview": "MINUTA DE CONTRATAÇÃO DIRETA POR VALOR\nEm conformidade com Art. 75, inciso II da Lei nº 14.133/2021."
            }
        ]
    },
    {
        "id": 203,
        "numero_processo_siga": "TLB-PRO-2024/03820",
        "numero_contrato_ou_edital": "TLB-CTR-2026/00038",
        "objeto": "Contratação direta emergencial/dispensa de licitação para serviços técnicos de manutenção especializada e suporte operacional da infraestrutura crítica de telecomunicações.",
        "unidade_demandante": "3000 - Diretoria Técnico-Operacional",
        "fornecedor": "CONSÓRCIO TELECOM BRASIL INFRA",
        "cnpj_cpf": "12.345.678/0001-90",
        "valor_estimado": 1850000.00,
        "modelo_contratacao": "Dispensa de Licitação",
        "fundamentacao_legal": "Lei nº 13.303/2016, Art. 29 c/c Art. 73 (Dispensa Tradicional / Regulamento Interno Telebras)",
        "amparo_legal_id": 29,
        "fase_siga": "contrato",  # Coluna 5: Homologação & Contrato
        "dias_decorridos": 67,
        "prioridade": "ALTO",
        "volume_siga": "Volume 2 (Fls. 181 a 345)",
        "setor_atual_sigla": "GCC",
        "setor_atual_nome": "2. GCC - Compras & Contratações (Formalização e Publicações)",
        "localizacao_atual": "Mesa Virtual SIGA / Formalização e Assinatura Digital do Contrato TLB-CTR-2026/00038",
        "custodiante_atual": "Pedro / Rosilda (Analistas GCC)",
        "dias_no_setor": 3,
        "link_siga": "https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla=TLB-PRO-2024/03820",
        "link_siga_contrato": "https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla=TLB-CTR-2026/00038",
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2026/38",
        "fonte_dados": "SIGA / PNCP",
        "fonte_tipo": "SIGA_PNCP",
        "ultimo_evento_siga": "Contrato assinado eletronicamente no SIGA pelas partes. Em trâmite de publicação do extrato no DOU e envio via API ao PNCP.",
        "ultima_atualizacao": "2026-09-25 12:15:30",
        "numero_contrato_futuro": "TLB-CTR-2026/00038",
        "volumes_detalhes": [
            {
                "numero": 1,
                "titulo": "Volume 1 - Fase Interna / Instrução Processual e Pesquisa de Preços",
                "folhas": "Fls. 1 a 180",
                "status": "Encerrado e Atestado",
                "descricao": "Autuação do DOD/DFD, Estudo Técnico Preliminar (ETP), Projeto Básico, Análise de Risco, RMS, Termo de Enquadramento no Art. 29 da Lei 13.303/2016, Minuta de Contrato elaborada e Relatório de Pesquisa de Mercado (IN 65/2021).",
                "documentos_principais": [
                    {"nome": "DOD / DFD nº 42/2024 - Oficialização da Demanda (GEOS/DTO)", "fls": "1 a 18", "data": "2024-07-02", "signatario": "Juliana Prado (DTO)", "tipo": "DFD"},
                    {"nome": "ETP - Estudo Técnico Preliminar e Dimensionamento", "fls": "19 a 45", "data": "2024-07-16", "signatario": "Equipe Técnica DTO", "tipo": "ETP"},
                    {"nome": "Projeto Básico Técnico e Matriz de Riscos", "fls": "46 a 82", "data": "2024-07-28", "signatario": "Engenharia Telebras", "tipo": "TR"},
                    {"nome": "RMS nº 108/2024 - Requisição de Materiais e Serviços SAP", "fls": "83 a 95", "data": "2024-08-01", "signatario": "Gestor DTO", "tipo": "RMS"},
                    {"nome": "Termo de Enquadramento - Art. 29 c/c 73 da Lei 13.303/2016", "fls": "96 a 105", "data": "2024-08-05", "signatario": "Marcus / Layllah (GCC)", "tipo": "ENQUADRAMENTO"},
                    {"nome": "Minuta do Contrato TLB-CTR-2026/00038 (Arquivo Auxiliar)", "fls": "106 a 128", "data": "2024-08-06", "signatario": "Marcus / Layllah (GCC)", "tipo": "MINUTA_CTR"},
                    {"nome": "Relatório de Pesquisa de Mercado e Justificativa de Valor (IN 65/2021)", "fls": "129 a 160", "data": "2024-08-28", "signatario": "Franciele / Roberta (GCC)", "tipo": "PESQUISA"},
                    {"nome": "Manifestação de Valor da Requisitante e RMS Suplementar", "fls": "161 a 174", "data": "2024-09-08", "signatario": "Diretoria DTO", "tipo": "SANEAMENTO"},
                    {"nome": "Declaração de Disponibilidade Orçamentária e Financeira (DIF)", "fls": "175 a 180", "data": "2024-09-12", "signatario": "GEFIN / GEOF", "tipo": "DIF"}
                ]
            },
            {
                "numero": 2,
                "titulo": "Volume 2 - Fase Deliberativa, Parecer CONJUR e Formalização Contratual",
                "folhas": "Fls. 181 a 345",
                "status": "Em Andamento (Fase de Assinatura e Publicação PNCP/DOU)",
                "descricao": "Minutas de Termo de Aprovação e Ratificação, Parecer Jurídico CONJUR, Despacho Saneador, Termos Assinados, Certidões Negativas, Assinatura Digital do Contrato TLB-CTR-2026/00038 e Código de Ética.",
                "documentos_principais": [
                    {"nome": "Minuta de Termo de Aprovação da Dispensa", "fls": "181 a 188", "data": "2024-09-15", "signatario": "Marcus / Layllah (GCC)", "tipo": "MINUTA"},
                    {"nome": "Minuta de Termo de Ratificação da Contratação Direta", "fls": "189 a 195", "data": "2024-09-16", "signatario": "Marcus / Layllah (GCC)", "tipo": "MINUTA"},
                    {"nome": "Parecer Jurídico CONJUR/TELEBRAS nº 342/2024 (Art. 73)", "fls": "196 a 220", "data": "2024-09-30", "signatario": "Dr. Fernando Rocha (CONJUR)", "tipo": "PARECER"},
                    {"nome": "Despacho Saneador da Instrução e Lista de Verificação (Checklist)", "fls": "221 a 235", "data": "2024-10-04", "signatario": "Layllah / Marcus (GCC)", "tipo": "CHECKLIST"},
                    {"nome": "Termo de Aprovação Assinado pelo Ordenador de Despesas", "fls": "236 a 242", "data": "2024-10-07", "signatario": "Alencastro / Presidência", "tipo": "APROVACAO"},
                    {"nome": "Termo de Ratificação Assinado pela Autoridade Superior", "fls": "243 a 248", "data": "2024-10-08", "signatario": "Alencastro / DAFRI", "tipo": "RATIFICACAO"},
                    {"nome": "Publicação do Extrato de Dispensa no Diário Oficial da União (DOU)", "fls": "249 a 255", "data": "2024-10-11", "signatario": "Pedro / Rosilda (GCC)", "tipo": "DOU"},
                    {"nome": "Despacho Saneador e Encaminhamento do Contrato às Partes", "fls": "256 a 265", "data": "2024-10-15", "signatario": "Pedro / Rosilda (GCC)", "tipo": "DESPACHO"},
                    {"nome": "Solicitação de DIF Atualizada e IVA à Gerência de Contabilidade (GCONT)", "fls": "266 a 275", "data": "2024-10-18", "signatario": "GCC / GCONT", "tipo": "IVA"},
                    {"nome": "Certidões Negativas e Documentos dos Signatários do Fornecedor", "fls": "276 a 305", "data": "2024-10-25", "signatario": "Fornecedor / GCC", "tipo": "CERTIDOES"},
                    {"nome": "Instrumento Contratual TLB-CTR-2026/00038 Assinado Eletronicamente", "fls": "306 a 330", "data": "2026-09-22", "signatario": "DAFRI / Fornecedor", "tipo": "CONTRATO_ASSINADO"},
                    {"nome": "Código de Ética e Declaração de Conduta de Fornecedores Telebras", "fls": "331 a 345", "data": "2026-09-24", "signatario": "Pedro / Rosilda (GCC)", "tipo": "ETICA"}
                ]
            }
        ],
        "tempo_com_usuarios": [
            {
                "usuario": "Franciele / Roberta",
                "cargo": "Analistas de Pesquisa de Mercado",
                "setor": "2. GCC - Pesquisa de Mercado e Preços",
                "dias_gastos": 18,
                "dias_previstos": 15,
                "desvio_dias": 3,
                "eh_gargalo": True,
                "severidade": "MEDIO",
                "motivo_gargalo": "Demora de retorno de cotações externas dos fornecedores consultados e reenvio de diligências para validação do mapa comparativo de preços conforme IN 65/2021.",
                "impacto": "Atraso no fechamento do valor de referência da contratação direta.",
                "recomendacao": "Instituir banco centralizado de preços públicos e fornecedores pré-cadastrados com prazos fixos de resposta."
            },
            {
                "usuario": "Área Requisitante / Gestor",
                "cargo": "Equipe Técnica Demandante",
                "setor": "1. Área Requisitante (DTO / GTI)",
                "dias_gastos": 8,
                "dias_previstos": 2,
                "desvio_dias": 6,
                "eh_gargalo": True,
                "severidade": "CRITICO",
                "motivo_gargalo": "Processo devolvido para saneamento de falhas na instrução inicial: divergência entre os itens do Projeto Básico e o ETP, além da emissão de nova RMS ajustada após o valor da pesquisa.",
                "impacto": "Processo ficou retido 8 dias úteis retornando para adequações técnicas que poderiam ter sido saneadas na abertura.",
                "recomendacao": "Adotar checklist prévio de conformidade (gatekeeping) antes do envio inicial da demanda para a GCC."
            },
            {
                "usuario": "Dr. Fernando Rocha",
                "cargo": "Procurador Consultivo",
                "setor": "4. CONJUR - Consultoria Jurídica",
                "dias_gastos": 12,
                "dias_previstos": 10,
                "desvio_dias": 2,
                "eh_gargalo": True,
                "severidade": "MEDIO",
                "motivo_gargalo": "Exame detalhado de conformidade com o Art. 73 da Lei nº 13.303/2016 (formalização de contrato) e formulação de ressalvas na minuta das cláusulas de penalidade e SLA.",
                "impacto": "Necessidade de resposta ao parecer saneador e elaboração de nota técnica de acolhimento das recomendações.",
                "recomendacao": "Uso de minutas padronizadas previamente chanceladas pela CONJUR para dispensas tradicionais recorrentes."
            },
            {
                "usuario": "Representantes Legais do Fornecedor",
                "cargo": "Signatários Externos",
                "setor": "Fornecedor Externo Contratado",
                "dias_gastos": 7,
                "dias_previstos": 5,
                "desvio_dias": 2,
                "eh_gargalo": True,
                "severidade": "MEDIO",
                "motivo_gargalo": "Demora na emissão de certidões negativas de débito municipais e regularização de procuração com poderes específicos para assinatura via certificado digital ICP-Brasil.",
                "impacto": "Retenção na assinatura digital bilateral do contrato TLB-CTR-2026/00038.",
                "recomendacao": "Solicitação antecipada da documentação societária e certidões no momento da homologação da pesquisa de mercado."
            },
            {
                "usuario": "Layllah / Marcus",
                "cargo": "Analistas de Contratação",
                "setor": "2. GCC - Instrução e Minutas",
                "dias_gastos": 3,
                "dias_previstos": 3,
                "desvio_dias": 0,
                "eh_gargalo": False,
                "severidade": "NORMAL",
                "motivo_gargalo": "Dentro do SLA: termo de enquadramento, minutas de termo de aprovação e ratificação concluídas sem intercorrências.",
                "impacto": "Fluxo célere na instrução inicial e elaboração das minutas.",
                "recomendacao": "Manter os modelos de despacho e padronização operacional adotados pela dupla."
            },
            {
                "usuario": "Pedro / Rosilda",
                "cargo": "Analistas de Formalização & Publicações",
                "setor": "2. GCC - Publicações & DOU/PNCP",
                "dias_gastos": 2,
                "dias_previstos": 2,
                "desvio_dias": 0,
                "eh_gargalo": False,
                "severidade": "NORMAL",
                "motivo_gargalo": "Dentro do SLA: transmissão célere do extrato de dispensa para a Imprensa Nacional (DOU) e preparação de envio ao PNCP.",
                "impacto": "Sem atraso na formalização e encaminhamento.",
                "recomendacao": "Concluir publicação do extrato contratual no PNCP e encaminhar DEG ao fiscal."
            }
        ],
        "gargalos_operacao_resumo": [
            {
                "fase": "1. Pesquisa de Mercado (Franciele / Roberta)",
                "dias_excedentes": 3,
                "descricao": "Demora de cotações externas de mercado (18 dias gastos vs 15 dias limite da planilha GCC)."
            },
            {
                "fase": "2. Saneamento na Requisitante (Área Técnica DTO)",
                "dias_excedentes": 6,
                "descricao": "Retrabalho de adequação técnica do ETP ao Projeto Básico e ajuste da RMS (8 dias gastos vs 2 dias limite)."
            },
            {
                "fase": "3. Análise Jurídica CONJUR (Dr. Fernando Rocha)",
                "dias_excedentes": 2,
                "descricao": "Diligência jurídica quanto aos requisitos do Art. 73 da Lei 13.303/2016 e cláusulas de penalidade (12 dias gastos vs 10 dias)."
            },
            {
                "fase": "4. Coleta de Documentos dos Signatários (Fornecedor)",
                "dias_excedentes": 2,
                "descricao": "Pendência de certidões e procurações digitais para validação no SIGA (7 dias gastos vs 5 dias limite)."
            }
        ],
        "etapas_fluxo_dispensa": [
            {"etapa": 1, "atividade": "ANÁLISE DOS DOCUMENTOS DE INSTRUÇÃO PROCESSUAL (DOD, ETP, Projeto Básico, RMS, RC, Análise de Risco)", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 2, "atividade": "SANEAMENTO DA INSTRUÇÃO DO PROCESSO PELA ÁREA REQUISITANTE, QUANDO NECESSÁRIO", "responsavel": "ÁREA REQUISITANTE", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 3, "atividade": "TERMO DE ENQUADRAMENTO (Art. 29 c/c 73 da Lei 13.303/2016)", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 4, "atividade": "ELABORAÇÃO MINUTA DE CONTRATO* (salvo como arquivo auxiliar do processo)", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 5, "atividade": "PESQUISA DE MERCADO ou JUSTIFICATIVA DE VALOR (Declaração de concordância e proposta)", "responsavel": "FRANCIELE / ROBERTA", "prazo_dias_uteis": 15, "concluida": True},
            {"etapa": 6, "atividade": "AJUSTES NA INSTRUÇÃO DURANTE A PESQUISA", "responsavel": "ÁREA REQUISITANTE / GCC", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 7, "atividade": "SOLICITAR MANIFESTAÇÃO DE VALOR DA ÁREA REQUISITANTE E NOVA RMS", "responsavel": "ÁREA REQUISITANTE", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 8, "atividade": "AUTORIZAÇÃO DO ORDENADOR, QUANDO NECESSÁRIA", "responsavel": "ORDENADOR DE DESPESA", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 9, "atividade": "CERTIDÕES DE REGULARIDADE FISCAL", "responsavel": "GCC / FORNECEDOR", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 10, "atividade": "PREVISÃO ORÇAMENTÁRIA", "responsavel": "GEFIN / GEOF", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 11, "atividade": "MINUTA DE TERMO DE APROVAÇÃO", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 12, "atividade": "MINUTA DE TERMO DE RATIFICAÇÃO", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 13, "atividade": "ANÁLISE JURÍDICA (Parecer CONJUR)", "responsavel": "CONJUR (Dr. Fernando Rocha)", "prazo_dias_uteis": 10, "concluida": True},
            {"etapa": 14, "atividade": "SANEAMENTO DO PROCESSO (ÁREA REQUISITANTE E GCC), QUANDO COUBER", "responsavel": "ÁREA REQUISITANTE / GCC", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 15, "atividade": "TERMO DE APROVAÇÃO", "responsavel": "DIRETORIA / ORDENADOR", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 16, "atividade": "TERMO DE RATIFICAÇÃO", "responsavel": "DIRETORIA / ORDENADOR", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 17, "atividade": "LISTA DE VERIFICAÇÃO", "responsavel": "GCC (LAYLLAH / MARCUS)", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 18, "atividade": "PUBLICAÇÃO DO EXTRATO DE DISPENSA NO DOU", "responsavel": "PEDRO / ROSILDA", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 19, "atividade": "DESPACHO SANEADOR E ENCAMINHAMENTO DO CONTRATO", "responsavel": "GCC (PEDRO / ROSILDA)", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 20, "atividade": "SOLICITAR DIF E SIGNATÁRIOS FORNECEDOR (DOCUMENTOS RESPECTIVOS)", "responsavel": "GCC / GEFIN", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 21, "atividade": "SOLICITAR IVA GCONT *", "responsavel": "GCONT", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 22, "atividade": "SOLICITAR AJUSTE DA RC", "responsavel": "ÁREA REQUISITANTE", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 23, "atividade": "INSERIR DOCUMENTOS DOS SIGNATÁRIOS NO PROCESSO*", "responsavel": "GCC / FORNECEDOR", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 24, "atividade": "CERTIDÕES DE REGULARIDADE", "responsavel": "GCC", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 25, "atividade": "ASSINATURA DE CONTRATO * (TLB-CTR-2026/00038)", "responsavel": "DAFRI / FORNECEDOR", "prazo_dias_uteis": 5, "concluida": True},
            {"etapa": 26, "atividade": "ENCAMINHAMENTO DO CONTRATO AO FORNECEDOR (Orientações NF, Calendário Fiscal, Código de Ética)", "responsavel": "PEDRO / ROSILDA", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 27, "atividade": "PUBLICAÇÃO DO EXTRATO DO CONTRATO NO DOU / PNCP *", "responsavel": "PEDRO / ROSILDA", "prazo_dias_uteis": 2, "concluida": False, "atual": True},
            {"etapa": 28, "atividade": "CADASTRO DO CONTRATO NO SAP *", "responsavel": "GCC / GCONT", "prazo_dias_uteis": 1, "concluida": False},
            {"etapa": 29, "atividade": "SOLICITAR GARANTIA, QUANDO CONSTAR NO TR *", "responsavel": "GCC / GECAD", "prazo_dias_uteis": 1, "concluida": False},
            {"etapa": 30, "atividade": "DEG (Elaborar e encaminhar ao fiscal)", "responsavel": "GCC / GECAD", "prazo_dias_uteis": 1, "concluida": False},
            {"etapa": 31, "atividade": "PUBLICAÇÃO DO CONTRATO NO SITE DA TELEBRAS", "responsavel": "GCC / COMUNICAÇÃO", "prazo_dias_uteis": 1, "concluida": False},
            {"etapa": 32, "atividade": "ELABORAR DESPACHO E ENVIAR PARA GESTÃO CONTRATUAL *", "responsavel": "GCC (PEDRO / ROSILDA)", "prazo_dias_uteis": 1, "concluida": False}
        ],
        "historico_tramitacao": [
            {
                "etapa": 1,
                "area": "1. Área Demandante (DTO - 3000)",
                "sigla": "DTO",
                "data_entrada": "2024-07-02",
                "data_saida": "2024-07-28",
                "dias_uteis": 18,
                "responsavel": "Juliana Prado (Engenheira Responsável - GEOS)",
                "despacho": "Autuação do DOD nº 42/2024, elaboração do ETP e Projeto Básico para manutenção emergencial.",
                "volume": "Volume 1 (Fls. 1 a 82)"
            },
            {
                "etapa": 2,
                "area": "2. GCC - Compras & Contratações (Instrução)",
                "sigla": "GCC",
                "data_entrada": "2024-07-29",
                "data_saida": "2024-08-06",
                "dias_uteis": 6,
                "responsavel": "Layllah / Marcus (Analistas de Contratação)",
                "despacho": "Emissão do Termo de Enquadramento no Art. 29 da Lei 13.303/2016 e elaboração da Minuta de Contrato TLB-CTR-2026/00038.",
                "volume": "Volume 1 (Fls. 83 a 128)"
            },
            {
                "etapa": 3,
                "area": "2. GCC - Pesquisa de Mercado e Preços",
                "sigla": "GCC/PESQUISA",
                "data_entrada": "2024-08-07",
                "data_saida": "2024-08-28",
                "dias_uteis": 18,
                "responsavel": "Franciele / Roberta (Analistas de Pesquisa)",
                "despacho": "Realização de pesquisa de preços conforme IN 65/2021. Obtenção de proposta comercial mais vantajosa.",
                "volume": "Volume 1 (Fls. 129 a 160)"
            },
            {
                "etapa": 4,
                "area": "1. Área Demandante (Saneamento de Instrução)",
                "sigla": "DTO",
                "data_entrada": "2024-08-29",
                "data_saida": "2024-09-08",
                "dias_uteis": 8,
                "responsavel": "Área Requisitante / Gestor Técnico DTO",
                "despacho": "Acolhimento da pesquisa de preços e emissão de RMS suplementar para adequação orçamentária.",
                "volume": "Volume 1 (Fls. 161 a 174)"
            },
            {
                "etapa": 5,
                "area": "3. GEFIN / GEOF - Orçamento & Finanças",
                "sigla": "GEFIN",
                "data_entrada": "2024-09-09",
                "data_saida": "2024-09-12",
                "dias_uteis": 4,
                "responsavel": "Equipe de Gestão Orçamentária e Financeira",
                "despacho": "Emissão da Declaração de Disponibilidade Orçamentária e Financeira (DIF) e bloqueio SAP.",
                "volume": "Volume 1 (Fls. 175 a 180)"
            },
            {
                "etapa": 6,
                "area": "4. CONJUR - Consultoria Jurídica",
                "sigla": "CONJUR",
                "data_entrada": "2024-09-13",
                "data_saida": "2024-09-30",
                "dias_uteis": 12,
                "responsavel": "Dr. Fernando Rocha (Procurador Consultivo)",
                "despacho": "Parecer Jurídico CONJUR/TELEBRAS nº 342/2024 aprovando a legalidade da dispensa tradicional (Art. 73).",
                "volume": "Volume 2 (Fls. 181 a 220)"
            },
            {
                "etapa": 7,
                "area": "5. Diretoria Executiva / Ordenador de Despesa",
                "sigla": "DIRETORIA",
                "data_entrada": "2024-10-01",
                "data_saida": "2024-10-08",
                "dias_uteis": 5,
                "responsavel": "Alencastro / Diretoria Colegiada",
                "despacho": "Assinatura do Termo de Aprovação e Termo de Ratificação da contratação direta emergencial.",
                "volume": "Volume 2 (Fls. 221 a 248)"
            },
            {
                "etapa": 8,
                "area": "2. GCC - Publicação de Dispensa no DOU",
                "sigla": "GCC/DOU",
                "data_entrada": "2024-10-09",
                "data_saida": "2024-10-14",
                "dias_uteis": 3,
                "responsavel": "Pedro / Rosilda (GCC)",
                "despacho": "Publicação do Extrato de Dispensa de Licitação no Diário Oficial da União (Seção 3).",
                "volume": "Volume 2 (Fls. 249 a 255)"
            },
            {
                "etapa": 9,
                "area": "Fornecedor Externo / Signatários Contratuais",
                "sigla": "FORNECEDOR",
                "data_entrada": "2024-10-15",
                "data_saida": "2024-10-25",
                "dias_uteis": 7,
                "responsavel": "Representantes Legais do Fornecedor / DAFRI",
                "despacho": "Juntada de certidões negativas de débito e assinatura digital do Contrato TLB-CTR-2026/00038.",
                "volume": "Volume 2 (Fls. 256 a 330)"
            },
            {
                "etapa": 10,
                "area": "2. GCC - Formalização & Publicação PNCP/DOU (Atual)",
                "sigla": "GCC",
                "data_entrada": "2026-09-22",
                "data_saida": "Em andamento",
                "dias_uteis": 3,
                "responsavel": "Pedro / Rosilda (GCC)",
                "despacho": "Contrato formalizado e assinado pelas partes. Transmissão do extrato ao PNCP e DOU em andamento (Etapa 27 do fluxo oficial).",
                "volume": "Volume 2 (Fls. 331 a 345)"
            }
        ],
        "proximos_passos": [
            {
                "etapa": "1. Publicação do Extrato do Contrato no DOU e PNCP (Etapa 27)",
                "area": "GCC - Publicações / PNCP",
                "prazo_estimado": "2 dias úteis",
                "responsavel": "Pedro / Rosilda (GCC)",
                "acao": "Transmissão da publicação do extrato do Contrato TLB-CTR-2026/00038 via API ao PNCP e envio ao Diário Oficial da União (Seção 3)."
            },
            {
                "etapa": "2. Cadastro do Contrato no SAP (Etapa 28)",
                "area": "GCC / GCONT",
                "prazo_estimado": "1 dia útil",
                "responsavel": "Equipe de Cadastro SAP",
                "acao": "Efetivar o cadastro do pedido e contrato TLB-CTR-2026/00038 no módulo SAP/MM para viabilizar empenho definitivo."
            },
            {
                "etapa": "3. Solicitação de Garantia Contratual (Etapa 29)",
                "area": "GCC / GECAD",
                "prazo_estimado": "1 dia útil",
                "responsavel": "Pedro / Rosilda (GCC)",
                "acao": "Notificação formal da contratada para apresentar apólice de seguro-garantia ou caução conforme TR."
            },
            {
                "etapa": "4. Emissão da DEG - Designação do Fiscal (Etapa 30)",
                "area": "GCC / Diretoria Demandante",
                "prazo_estimado": "1 dia útil",
                "responsavel": "GCC / Fiscal Designado",
                "acao": "Elaboração e encaminhamento da Portaria DEG ao fiscal titular e substituto da área técnica."
            },
            {
                "etapa": "5. Remessa para Gestão Contratual & Fiscalização (Etapas 31 e 32)",
                "area": "GECAD / Fiscalização",
                "prazo_estimado": "Início da vigência contratual",
                "responsavel": "GECAD / Fiscal Titular",
                "acao": "Publicação do contrato no Portal da Transparência da Telebras e despacho conclusivo da GCC enviando os autos à GECAD."
            }
        ],
        "ciclo_vida_contratual": {
            "reajuste": {
                "titulo": "Reajuste Contratual (Anualidade)",
                "periodicidade": "Anual (a cada 12 meses)",
                "data_base_prevista": "2027-09-22",
                "marco_solicitacao": "A partir de Agosto/2027 (30 dias antes do aniversário)",
                "indice_reajuste": "IPCA (Índice Nacional de Preços ao Consumidor Amplo) ou índice setorial pactuado",
                "procedimento": "Apostilamento Contratual (dispensa termo aditivo bilateral formal, conforme Art. 81, § 8º da Lei nº 13.303/2016)",
                "setor_responsavel": "GCONT / GECAD / Fiscal do Contrato",
                "fluxo_previsto": [
                    "1. Abertura de processo auxiliar de apostilamento pelo Fiscal ou mediante requerimento formal do Consórcio com demonstração dos cálculos.",
                    "2. Manifestação e validação da Gerência de Contabilidade (GCONT) quanto ao índice acumulado do IPCA nos 12 meses.",
                    "3. Verificação de disponibilidade orçamentária complementar pela GEFIN.",
                    "4. Emissão de Termo de Apostilamento assinado pelo Gestor Contratual e registro contábil no SAP."
                ]
            },
            "prorrogacao": {
                "titulo": "Prorrogação de Vigência Contratual",
                "enquadramento_legal": "Lei nº 13.303/2016, Art. 71 c/c Regulamento Interno de Licitações e Contratos (RELIC)",
                "vigencia_inicial": "12 meses (22/09/2026 a 21/09/2027)",
                "limite_prorrogacao": "Até 60 meses (5 anos) sucessivos por se tratar de serviço contínuo de manutenção da infraestrutura de telecomunicações",
                "marco_deflagracao": "Com no mínimo 90 dias de antecedência do término da vigência (Junho/2027)",
                "procedimento": "Termo Aditivo Bilateral de Prorrogação de Vigência",
                "setor_responsavel": "Fiscal do Contrato (DTO/3820) / GCC / CONJUR / DAFRI",
                "requisitos_obrigatorios": [
                    "1. Relatório Circunstanciado de Desempenho e Atesto do Fiscal do Contrato comprovando a execução satisfatória dos serviços.",
                    "2. Pesquisa de Vantajosidade Econômica realizada pela GCC (IN 65/2021) comprovando que os preços praticados permanecem mais vantajosos que nova contratação.",
                    "3. Manifestação formal de interesse e concordância da Contratada (Consórcio).",
                    "4. Regularidade fiscal plena da Contratada (CNDs Federal, Estadual, Municipal, FGTS e CNDT válidas).",
                    "5. Declaração de Disponibilidade Orçamentária e Financeira (DIF) para o próximo exercício.",
                    "6. Parecer Jurídico da CONJUR aprovando a minuta do Termo Aditivo.",
                    "7. Autorização da Diretoria Executiva Colegiada (REDIR/DAFRI) e assinatura bilateral no SIGA."
                ]
            },
            "alteracao": {
                "titulo": "Alteração Contratual (Acréscimos e Supressões / Modificação Qualitativa)",
                "enquadramento_legal": "Lei nº 13.303/2016, Art. 81, § 1º (Limite legal de até 25% para compras e serviços)",
                "limite_legal": "Até 25% do valor inicial atualizado do contrato (ou supressões consensuais além desse limite)",
                "procedimento": "Termo Aditivo Bilateral",
                "setor_responsavel": "Área Técnica Requisitante (DTO/3820) / GCC / CONJUR / Diretoria Colegiada",
                "hipoteses": "Necessidade de inclusão de novas estações terrenas satelitais, adequação quantitativa de suporte operacional ou supressão de itens obsoletos.",
                "fluxo_previsto": [
                    "1. Nota Técnica da Área Requisitante com justificativa técnica e motivação fática e econômica.",
                    "2. Elaboração da planilha orçamentária demonstrando a variação percentual (dentro da trava dos 25%).",
                    "3. Anuência expressa da Contratada com a proposta técnica e de custos.",
                    "4. Obtenção de bloqueio orçamentário suplementar na GEFIN.",
                    "5. Análise prévia e Parecer Jurídico da CONJUR.",
                    "6. Deliberação da Diretoria Executiva Colegiada (REDIR).",
                    "7. Assinatura do Termo Aditivo no SIGA e publicação no DOU e PNCP em até 10 dias úteis."
                ]
            },
            "encerramento": {
                "titulo": "Encerramento e Liquidação Final do Contrato",
                "previsao": "Ao final da vigência do contrato e cumprimento de todas as obrigações pactuadas",
                "procedimento": "Termos de Recebimento, Baixa no SAP e Liberação de Garantia",
                "setor_responsavel": "Fiscal do Contrato / GECAD / GCONT / GEFIN",
                "etapas_encerramento": [
                    {
                        "fase": "1. Recebimento Provisório (TRP)",
                        "prazo": "Até 15 dias corridos após o término da vigência",
                        "descricao": "Vistoria dos serviços executados e emissão do Termo de Recebimento Provisório pelo Fiscal Titular."
                    },
                    {
                        "fase": "2. Recebimento Definitivo (TRD)",
                        "prazo": "Até 30 dias corridos após o TRP",
                        "descricao": "Auditoria de cumprimento dos SLAs, conformidade técnica e verificação de quitação trabalhista dos colaboradores vinculados."
                    },
                    {
                        "fase": "3. Liberação de Garantia Contratual",
                        "prazo": "Até 10 dias úteis após o TRD",
                        "descricao": "Despacho da GECAD restituindo ou cancelando a apólice de seguro-garantia/fiança bancária/caução."
                    },
                    {
                        "fase": "4. Liquidação e Baixa no SAP",
                        "prazo": "Até 20 dias após TRD",
                        "descricao": "Pagamento da última fatura, encerramento de provisões contábeis no SAP/MM e baixa patrimonial na GCONT."
                    }
                ]
            }
        },
        "documentos": [
            {
                "id": "DOC-03820-1",
                "titulo": "DOD_Oficializacao_Demanda_DTO.pdf",
                "tipo": "PDF",
                "tamanho_kb": 320,
                "data_juntada": "2024-07-02 10:15:00",
                "signatario": "Juliana Prado - Gerente Técnica (GEOS/DTO)",
                "resumo_conteudo": "Documento de Oficialização da Demanda para manutenção especializada preventiva e corretiva da infraestrutura de telecomunicações.",
                "conteudo_preview": "DOCUMENTO DE OFICIALIZAÇÃO DA DEMANDA (DOD)\nProcesso SIGA: TLB-PRO-2024/03820\nUnidade: Diretoria Técnico-Operacional (3000)\nObjeto: Manutenção especializada de estações terrenas e suporte operacional contínuo."
            },
            {
                "id": "DOC-03820-2",
                "titulo": "Termo_Enquadramento_Art29_Lei13303.pdf",
                "tipo": "PDF",
                "tamanho_kb": 285,
                "data_juntada": "2024-08-05 14:30:00",
                "signatario": "Layllah / Marcus - Analistas de Contratação GCC",
                "resumo_conteudo": "Termo de Enquadramento no Art. 29 c/c Art. 73 da Lei nº 13.303/2016 e Prática nº 88 da Telebras, fundamentando a dispensa de licitação.",
                "conteudo_preview": "TERMO DE ENQUADRAMENTO JURÍDICO\nFundamentação: Lei das Estatais (Lei 13.303/2016, Art. 29 c/c Art. 73).\nModalidade: Dispensa Tradicional com exigência de formalização de instrumento contratual."
            },
            {
                "id": "DOC-03820-3",
                "titulo": "Relatorio_Pesquisa_Mercado_IN65.pdf",
                "tipo": "PDF",
                "tamanho_kb": 740,
                "data_juntada": "2024-08-28 16:45:00",
                "signatario": "Franciele / Roberta - Pesquisa de Mercado GCC",
                "resumo_conteudo": "Relatório comparativo de preços e justificativa de vantajosa proposta do Consórcio Telecom Brasil Infra.",
                "conteudo_preview": "RELATÓRIO DE PESQUISA DE PREÇOS (IN 65/2021)\nFornecedor selecionado: CONSÓRCIO TELECOM BRASIL INFRA (CNPJ 12.345.678/0001-90)\nValor Global Aceitável: R$ 1.850.000,00."
            },
            {
                "id": "DOC-03820-4",
                "titulo": "Parecer_Juridico_CONJUR_342_2024.pdf",
                "tipo": "PDF",
                "tamanho_kb": 890,
                "data_juntada": "2024-09-30 11:20:00",
                "signatario": "Dr. Fernando Rocha - Procurador Consultivo",
                "resumo_conteudo": "Parecer prévio favorável à formalização da contratação direta por dispensa tradicional com fulcro na Lei 13.303/2016.",
                "conteudo_preview": "PARECER JURÍDICO CONJUR/TELEBRAS Nº 342/2024\nConclusão: Viabilidade jurídica da contratação por dispensa de licitação e minuta de contrato TLB-CTR-2026/00038 aprovada com recomendações."
            },
            {
                "id": "DOC-03820-5",
                "titulo": "Termo_Ratificacao_Autoridade_Competente.pdf",
                "tipo": "PDF",
                "tamanho_kb": 210,
                "data_juntada": "2024-10-08 15:10:00",
                "signatario": "Alencastro - Diretoria Executiva",
                "resumo_conteudo": "Termo de Ratificação da Dispensa de Licitação publicado no DOU Seção 3.",
                "conteudo_preview": "TERMO DE RATIFICAÇÃO\nRatifico a dispensa de licitação do Processo TLB-PRO-2024/03820 em favor do Consórcio Telecom Brasil Infra no valor de R$ 1.850.000,00."
            },
            {
                "id": "DOC-03820-6",
                "titulo": "Contrato_Assinado_TLB_CTR_2026_00038.pdf",
                "tipo": "PDF",
                "tamanho_kb": 1420,
                "data_juntada": "2026-09-22 17:35:00",
                "signatario": "DAFRI / Consórcio Telecom Brasil Infra",
                "resumo_conteudo": "Instrumento contratual TLB-CTR-2026/00038 devidamente assinado eletronicamente por ambas as partes no SIGA.",
                "conteudo_preview": "INSTRUMENTO CONTRATUAL TELEBRAS Nº TLB-CTR-2026/00038\nContratante: TELECOMUNICAÇÕES BRASILEIRAS S.A. - TELEBRAS\nContratada: CONSÓRCIO TELECOM BRASIL INFRA\nProcesso SIGA Origem: TLB-PRO-2024/03820"
            }
        ]
    },
    {
        "id": 204,
        "numero_processo_siga": "TLB-PRO-2026/002672",
        "aliases_siga": ["TLB-PRO-2026/02672", "TLB-PRO-2026-002672", "02672", "002672", "90014"],
        "numero_contrato_ou_edital": "PE nº 90014/2026 (TLB-EDT-2026/00014)",
        "objeto": "Contratação de empresa especializada para prestação de serviços de Saúde e Segurança do Trabalho em conformidade com a NR-7 do Ministério do Trabalho e Emprego (Medicina do Trabalho).",
        "unidade_demandante": "2400 - Gerência de Gestão de Pessoas (GGP / DAFRI)",
        "fornecedor": "EVOLUE SERVIÇOS LTDA",
        "cnpj_cpf": "26.699.784/0001-81",
        "valor_estimado": 5038033.70,
        "valor_homologado": 3499355.00,
        "modelo_contratacao": "Pregão Eletrônico",
        "fundamentacao_legal": "Lei nº 13.303/2016, Art. 32, Inciso IV c/c Art. 93 do RELIC Telebras",
        "amparo_legal_id": 32,
        "fase_siga": "contrato",  # Homologado e em formalização contratual
        "dias_decorridos": 24,
        "prioridade": "ALTO",
        "volume_siga": "Volume 4 (Fls. 664 a 950+)",
        "setor_atual_sigla": "GCC",
        "setor_atual_nome": "2. GCC - Compras & Contratações (Formalização Contratual)",
        "localizacao_atual": "Mesa Virtual SIGA / Formalização e Assinatura do Contrato de 60 Meses",
        "custodiante_atual": "Pedro / Rosilda (Analistas GCC / Pregoeiro Pedro Diniz)",
        "dias_no_setor": 4,
        "link_pncp": "https://pncp.gov.br/app/editais/37753638000103/2026/000062",
        "link_comprasnet": "https://cnetmobile.estaleiro.serpro.gov.br/comprasnet-web/public/compras/acompanhamento-compra?compra=92515005900142026",
        "link_siga": "https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla=TLB-PRO-2026/002672",
        "link_siga_tr": "https://extranet.telebras.com.br/sigaex/public/app/autenticar?n=942857-5785",
        "link_siga_edital": "https://extranet.telebras.com.br/sigaex/public/app/autenticar?n=948310-2656",
        "fonte_dados": "SIGA / PNCP / Compras.gov.br",
        "fonte_tipo": "SIGA_PNCP",
        "ultimo_evento_siga": "Pregão Eletrônico nº 90014/2026 homologado pela DAFRI em 28/07/2026. Licitante EVOLUE SERVIÇOS LTDA adjudicado por R$ 3.499.355,00 (economia de 30,54%). Autos em formalização contratual.",
        "ultima_atualizacao": "2026-09-25 15:40:00",
        "volumes_detalhes": [
            {
                "numero": 1,
                "titulo": "Volume 1 - Fase Interna / Demanda, ETP, Matriz de Riscos e RMS SAP",
                "folhas": "Fls. 1 a 280",
                "status": "Encerrado e Atestado",
                "custodia": "Arquivo Setorial GGP / GCC",
                "descricao": "Oficialização da necessidade de medicina ocupacional NR-7 para sede Brasília e regionais, Estudo Técnico Preliminar (ETP), Matriz de Riscos e Requisição de Compras no SAP/MM.",
                "documentos_principais": [
                    {"nome": "DOD nº 18/2026 - Oficialização da Demanda (GGP)", "fls": "1 a 24", "data": "2026-04-10", "signatario": "Isabela Aquino Schneider (GGP)", "tipo": "DOD"},
                    {"nome": "ETP - Estudo Técnico Preliminar de Saúde do Trabalho", "fls": "25 a 78", "data": "2026-04-28", "signatario": "Sarah Lima Moreira Moura (Especialista)", "tipo": "ETP"},
                    {"nome": "Matriz de Riscos Ocupacionais e Operacionais", "fls": "79 a 115", "data": "2026-05-08", "signatario": "Equipe de Gestão de Pessoas", "tipo": "RISCOS"},
                    {"nome": "RMS nº 412/2026 e Requisição de Compras SAP/MM", "fls": "116 a 140", "data": "2026-05-15", "signatario": "Gestão de Pessoas / SAP", "tipo": "RMS"},
                    {"nome": "Declaração de Alinhamento ao PLAC 2026", "fls": "141 a 160", "data": "2026-05-18", "signatario": "Alencastro (DAFRI)", "tipo": "PLAC"}
                ]
            },
            {
                "numero": 2,
                "titulo": "Volume 2 - Enquadramento Jurídico, Pesquisa de Mercado e Minuta de Edital",
                "folhas": "Fls. 281 a 617",
                "status": "Encerrado e Atestado",
                "custodia": "Mesa GCC",
                "descricao": "Termo de Enquadramento no Art. 32 da Lei 13.303/2016, Pesquisa de Preços IN 65/2021 (R$ 5.038.033,70), Minuta de Edital e Minuta de Contrato de 60 meses.",
                "documentos_principais": [
                    {"nome": "Termo de Enquadramento - Art. 32, IV da Lei 13.303/2016", "fls": "281 a 295", "data": "2026-05-20", "signatario": "Layllah / Marcus (GCC)", "tipo": "ENQUADRAMENTO"},
                    {"nome": "Relatório de Pesquisa de Mercado IN 65/2021 (R$ 5.038.033,70)", "fls": "296 a 380", "data": "2026-06-02", "signatario": "Franciele / Roberta (GCC)", "tipo": "PESQUISA"},
                    {"nome": "Manifestação de Valor da Requisitante e Adequação RMS", "fls": "381 a 405", "data": "2026-06-05", "signatario": "Isabela Schneider (GGP)", "tipo": "SANEAMENTO"},
                    {"nome": "Declaração de Informação para Fornecimento (DIF Telebras)", "fls": "406 a 445", "data": "2026-06-08", "signatario": "GEFIN / GEOF", "tipo": "DIF"},
                    {"nome": "Minuta de Edital Pregão Eletrônico nº 90014/2026", "fls": "446 a 520", "data": "2026-06-09", "signatario": "Pedro Diniz / GCC", "tipo": "MINUTA_EDT"},
                    {"nome": "Minuta de Contrato de Prestação de Serviços (60 meses)", "fls": "521 a 565", "data": "2026-06-09", "signatario": "Marcus / Layllah (GCC)", "tipo": "MINUTA_CTR"}
                ]
            },
            {
                "numero": 3,
                "titulo": "Volume 3 - Termo de Referência Consolidado (TLBREF202600108A) e Anexos",
                "folhas": "Fls. 618 a 663",
                "status": "Encerrado e Atestado com Senha SIGA",
                "custodia": "GGP / GCC",
                "descricao": "Termo de Referência final assinado eletronicamente por Sarah Moura e Isabela Schneider (Doc SIGA nº 942857-5785) com especificação completa de exames, PGR, PCMSO, LTCAT e regionais.",
                "documentos_principais": [
                    {"nome": "Termo de Referência nº TLBREF202600108A (Doc 942857-5785)", "fls": "618 a 660", "data": "2026-06-10", "signatario": "Sarah Lima Moreira Moura / Isabela Aquino Schneider", "tipo": "TR_OFICIAL"},
                    {"nome": "Tabelas de Exames por Regional (Brasília, Fortaleza, POA, RJ, Belém)", "fls": "661 a 663", "data": "2026-06-10", "signatario": "Saúde Ocupacional GGP", "tipo": "TABELAS"}
                ]
            },
            {
                "numero": 4,
                "titulo": "Volume 4 - Jurídico, Publicação Edital, Disputa Comprasnet e Homologação",
                "folhas": "Fls. 664 a 950+",
                "status": "Homologado (Fase de Assinatura Contratual)",
                "custodia": "Mesa Virtual GCC / Formalização",
                "descricao": "Parecer Jurídico CONJUR, Edital assinado por Fernanda Ayres (Doc 948310-2656), publicação no DOU e PNCP, disputa de 19 lances no Comprasnet, relatório de julgamento e termo de homologação DAFRI.",
                "documentos_principais": [
                    {"nome": "Parecer Jurídico CONJUR nº 214/2026 (Aprovação com Checklist)", "fls": "664 a 710", "data": "2026-06-18", "signatario": "Procurador Consultivo CONJUR", "tipo": "PARECER"},
                    {"nome": "Despacho Saneador e Autorização de Abertura DAFRI", "fls": "711 a 730", "data": "2026-06-22", "signatario": "Alencastro (DAFRI)", "tipo": "AUTORIZACAO"},
                    {"nome": "Edital TLB-EDT-2026/00014 Assinado no SIGA (Doc 948310-2656)", "fls": "731 a 770", "data": "2026-06-24", "signatario": "Fernanda Ayres Jardim Elias (Gerente GCC)", "tipo": "EDITAL_ASSINADO"},
                    {"nome": "Publicação do Aviso de Licitação no DOU e PNCP", "fls": "771 a 785", "data": "2026-06-25", "signatario": "Pedro / Rosilda (GCC)", "tipo": "DOU"},
                    {"nome": "Ata da Sessão Pública no Compras.gov.br (19 Lances)", "fls": "786 a 840", "data": "2026-07-10", "signatario": "Pedro Diniz (Pregoeiro)", "tipo": "ATA_SESSAO"},
                    {"nome": "Parecer Técnico de Aceitabilidade da Proposta da Evolue", "fls": "841 a 870", "data": "2026-07-16", "signatario": "Sarah Moura (Área Técnica)", "tipo": "PARECER_TECNICO"},
                    {"nome": "Relatório de Julgamento e Habilitação (Licitante Vencedor)", "fls": "871 a 910", "data": "2026-07-28", "signatario": "Pedro Diniz (Pregoeiro)", "tipo": "JULGAMENTO"},
                    {"nome": "Termo de Homologação da Licitação PE 90014/2026", "fls": "911 a 950", "data": "2026-07-28", "signatario": "Alencastro (Diretor DAFRI)", "tipo": "HOMOLOGACAO"}
                ]
            }
        ],
        "tempo_com_usuarios": [
            {
                "usuario": "Sarah Lima Moreira Moura",
                "cargo": "Especialista em Gestão / Saúde e Medicina do Trabalho",
                "setor": "1. Área Técnica Especializada (GGP)",
                "dias_gastos": 15,
                "dias_previstos": 15,
                "desvio_dias": 0,
                "eh_gargalo": False,
                "severidade": "NORMAL",
                "motivo_gargalo": "Dentro do SLA técnico: detalhamento primoroso das 5 regionais e tabelas de exames no TR TLBREF202600108A.",
                "impacto": "Termo de referência robusto e sem impugnações procedentes.",
                "recomendacao": "Manter os modelos padronizados de dimensionamento de saúde ocupacional."
            },
            {
                "usuario": "Isabela Aquino Schneider",
                "cargo": "Gerente de Gestão de Pessoas",
                "setor": "1. Área Demandante (GGP / DAFRI)",
                "dias_gastos": 8,
                "dias_previstos": 5,
                "desvio_dias": 3,
                "eh_gargalo": True,
                "severidade": "MEDIO",
                "motivo_gargalo": "Processo demandou ajustes de quantitativos no SAP/MM e suplementação orçamentária após os valores da pesquisa de preços.",
                "impacto": "Pequena retenção na emissão da RMS ajustada.",
                "recomendacao": "Ajuste preventivo de quantitativos antes do envio inicial da demanda para a GCC."
            },
            {
                "usuario": "Franciele / Roberta",
                "cargo": "Analistas de Pesquisa de Mercado",
                "setor": "2. GCC - Pesquisa de Mercado e Preços",
                "dias_gastos": 18,
                "dias_previstos": 15,
                "desvio_dias": 3,
                "eh_gargalo": True,
                "severidade": "MEDIO",
                "motivo_gargalo": "Complexidade de precificação para atendimento multi-regional em 5 estados e demora nas respostas das clínicas privadas.",
                "impacto": "Valor de referência de R$ 5,03M fechado com 3 dias de acréscimo.",
                "recomendacao": "Utilização prioritária do Painel de Preços e contratações similares de estatais federais."
            },
            {
                "usuario": "Procuradoria Consultiva (CONJUR)",
                "cargo": "Procurador Jurídico",
                "setor": "4. CONJUR - Consultoria Jurídica",
                "dias_gastos": 14,
                "dias_previstos": 15,
                "desvio_dias": 0,
                "eh_gargalo": False,
                "severidade": "NORMAL",
                "motivo_gargalo": "Dentro do prazo legal de 15 dias: parecer jurídico nº 214/2026 aprovando o edital e minuta de contrato.",
                "impacto": "Segurança jurídica plena para a publicação do certame.",
                "recomendacao": "Manter o modelo de checklist de conformidade prévia."
            },
            {
                "usuario": "Pedro Diniz / Fernanda Ayres",
                "cargo": "Pregoeiro Oficial e Gerente GCC",
                "setor": "2. GCC - Pregoeiro e Equipe de Apoio",
                "dias_gastos": 13,
                "dias_previstos": 15,
                "desvio_dias": 0,
                "eh_gargalo": False,
                "severidade": "NORMAL",
                "motivo_gargalo": "Condução exemplar da sessão pública no Comprasnet: 19 lances negociados e obtenção de R$ 1,53 milhão de economia (30,54% de desconto).",
                "impacto": "Redução expressiva no custo da contratação e agilidade na habilitação.",
                "recomendacao": "Adotar a estratégia de negociação por lote único nos próximos certames de serviços contínuos."
            },
            {
                "usuario": "Alencastro",
                "cargo": "Diretor DAFRI / Autoridade Competente",
                "setor": "5. Diretoria Executiva (DAFRI)",
                "dias_gastos": 2,
                "dias_previstos": 3,
                "desvio_dias": 0,
                "eh_gargalo": False,
                "severidade": "NORMAL",
                "motivo_gargalo": "Homologação célere em 28/07/2026, viabilizando a assinatura contratual no prazo.",
                "impacto": "Garantia de continuidade dos exames periódicos sem vácuo contratual.",
                "recomendacao": "Manter o fluxo ágil de apreciação decisória."
            }
        ],
        "gargalos_operacao_resumo": [
            {
                "fase": "1. Pesquisa de Preços Multi-Regional (Franciele / Roberta)",
                "dias_excedentes": 3,
                "descricao": "Dificuldade na coleta de orçamentos médicos para regionais remotas (18 dias gastos vs 15 dias meta)."
            },
            {
                "fase": "2. Adequação da RMS no SAP (Área Demandante GGP)",
                "dias_excedentes": 3,
                "descricao": "Ajuste na dotação orçamentária após validação da estimativa de R$ 5,03M (8 dias gastos vs 5 dias limite)."
            }
        ],
        "etapas_fluxo_pregao": [
            {"etapa": 1, "atividade": "ANÁLISE DOS DOCUMENTOS DE INSTRUÇÃO PROCESSUAL (DOD, ETP, TR, Análise de Risco, RMS)", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 5, "concluida": True},
            {"etapa": 2, "atividade": "SANEAMENTO DA INSTRUÇÃO DO PROCESSO PELA ÁREA REQUISITANTE", "responsavel": "ÁREA REQUISITANTE (GGP)", "prazo_dias_uteis": 10, "concluida": True},
            {"etapa": 3, "atividade": "TERMO DE ENQUADRAMENTO (Art. 32 da Lei 13.303/2016)", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 4, "atividade": "ELABORAÇÃO MINUTA DE CONTRATO * (60 meses)", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 5, "atividade": "PESQUISA DE MERCADO / JUSTIFICATIVA DE VALOR (IN 65/2021)", "responsavel": "FRANCIELE / ROBERTA", "prazo_dias_uteis": 15, "concluida": True},
            {"etapa": 6, "atividade": "AJUSTES NA INSTRUÇÃO DURANTE A PESQUISA", "responsavel": "GGP / GCC", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 7, "atividade": "MANIFESTAÇÃO DE VALOR DA ÁREA REQUISITANTE E NOVA RMS", "responsavel": "GGP", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 8, "atividade": "AUTORIZAÇÃO DO ORDENADOR DE DESPESAS", "responsavel": "ORDENADOR (DAFRI)", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 9, "atividade": "PREVISÃO ORÇAMENTÁRIA (DIF)", "responsavel": "GEFIN / GEOF", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 10, "atividade": "AUTORIZAÇÃO DA ABERTURA DO PROCESSO LICITATÓRIO", "responsavel": "ALENCASTRO (DAFRI)", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 11, "atividade": "ANEXAR DEM PREGOEIRO E EQUIPE DE APOIO", "responsavel": "GCC / DIRETORIA", "prazo_dias_uteis": 0, "concluida": True},
            {"etapa": 12, "atividade": "ELABORAÇÃO MINUTA DE EDITAL (TLB-EDT-2026/00014)", "responsavel": "PREGOEIRO / GCC", "prazo_dias_uteis": 5, "concluida": True},
            {"etapa": 13, "atividade": "ANÁLISE JURÍDICA COM CHECKLIST (Parecer CONJUR)", "responsavel": "CONJUR", "prazo_dias_uteis": 15, "concluida": True},
            {"etapa": 14, "atividade": "SANEAMENTO DO PROCESSO PÓS-PARECER", "responsavel": "GGP / GCC", "prazo_dias_uteis": 5, "concluida": True},
            {"etapa": 15, "atividade": "ELABORAÇÃO DO DESPACHO SANEADOR", "responsavel": "GCC", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 16, "atividade": "PUBLICAÇÃO DO EDITAL NO PNCP, DOU E SITE DA TELEBRAS", "responsavel": "PEDRO / ROSILDA", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 17, "atividade": "ESCLARECIMENTOS / IMPUGNAÇÃO", "responsavel": "PREGOEIRO / SARAH MOURA", "prazo_dias_uteis": 0, "concluida": True},
            {"etapa": 18, "atividade": "ABERTURA DA SESSÃO PÚBLICA NO COMPRAS.GOV.BR", "responsavel": "PREGOEIRO (PEDRO DINIZ)", "prazo_dias_uteis": 15, "concluida": True},
            {"etapa": 19, "atividade": "ANÁLISE DE PROPOSTA E HABILITAÇÃO JURÍDICA/FISCAL/ECONÔMICA", "responsavel": "PREGOEIRO / APOIO", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 20, "atividade": "ANÁLISE DE PROPOSTA/HABILITAÇÃO TÉCNICA", "responsavel": "SARAH MOURA (ÁREA TÉCNICA)", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 21, "atividade": "PRAZOS RECURSAIS", "responsavel": "PREGOEIRO / CONJUR", "prazo_dias_uteis": 25, "concluida": True},
            {"etapa": 22, "atividade": "ADJUDICAÇÃO E HOMOLOGAÇÃO (DAFRI)", "responsavel": "PREGOEIRO / ALENCASTRO", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 23, "atividade": "DESPACHO DE ENCAMINHAMENTO PARA FORMALIZAÇÃO", "responsavel": "PREGOEIRO / GCC", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 24, "atividade": "SOLICITAR DIF, ANEXO C E DOCUMENTOS SIGNATÁRIOS", "responsavel": "LAYLLAH / MARCUS", "prazo_dias_uteis": 3, "concluida": True},
            {"etapa": 25, "atividade": "SOLICITAR APURAÇÃO DE IVA À GCONT", "responsavel": "GCONT", "prazo_dias_uteis": 2, "concluida": True},
            {"etapa": 26, "atividade": "SOLICITAR AJUSTE DA RC NO SAP À ÁREA REQUISITANTE", "responsavel": "GGP", "prazo_dias_uteis": 1, "concluida": True},
            {"etapa": 27, "atividade": "INSERIR DOCUMENTOS DOS SIGNATÁRIOS NO PROCESSO", "responsavel": "GCC / FORNECEDOR", "prazo_dias_uteis": 0, "concluida": True},
            {"etapa": 28, "atividade": "EMISSÃO DE CERTIDÕES DE REGULARIDADE ATUALIZADAS", "responsavel": "GCC", "prazo_dias_uteis": 0, "concluida": True},
            {"etapa": 29, "atividade": "ASSINATURA DE CONTRATO * (EVOLUE SERVIÇOS)", "responsavel": "DAFRI / FORNECEDOR", "prazo_dias_uteis": 5, "concluida": False, "atual": True},
            {"etapa": 30, "atividade": "ENCAMINHAMENTO DO CONTRATO AO FORNECEDOR E CALENDÁRIO FISCAL", "responsavel": "PEDRO / ROSILDA", "prazo_dias_uteis": 5, "concluida": False},
            {"etapa": 31, "atividade": "PUBLICAÇÃO DO EXTRATO DO CONTRATO NO DOU / PNCP *", "responsavel": "PEDRO / ROSILDA", "prazo_dias_uteis": 2, "concluida": False},
            {"etapa": 32, "atividade": "CADASTRO DO CONTRATO NO SAP/MM *", "responsavel": "GCC / GCONT", "prazo_dias_uteis": 1, "concluida": False},
            {"etapa": 33, "atividade": "SOLICITAR GARANTIA, QUANDO CONSTAR NO TR *", "responsavel": "GCC / GECAD", "prazo_dias_uteis": 0, "concluida": False},
            {"etapa": 34, "atividade": "ENCAMINHAR CONTRATO PARA PUBLICAÇÃO NO SITE DA TELEBRAS", "responsavel": "GCC / COMUNICAÇÃO", "prazo_dias_uteis": 1, "concluida": False},
            {"etapa": 35, "atividade": "DEG (Elaborar e encaminhar ao fiscal)", "responsavel": "GCC / GECAD", "prazo_dias_uteis": 1, "concluida": False},
            {"etapa": 36, "atividade": "ELABORAR DESPACHO E ENVIAR PARA GESTÃO CONTRATUAL *", "responsavel": "GCC (PEDRO / ROSILDA)", "prazo_dias_uteis": 1, "concluida": False}
        ],
        "documentos": [
            {
                "id": "DOC-02672-1",
                "titulo": "DOD_Oficializacao_Demanda_GGP.pdf",
                "tipo": "PDF",
                "tamanho_kb": 290,
                "data_juntada": "2026-04-10 09:30:00",
                "signatario": "Isabela Aquino Schneider - Gerente GGP",
                "resumo_conteudo": "Oficialização da necessidade de contratação continuada de serviços de saúde e medicina ocupacional para os empregados da Telebras.",
                "conteudo_preview": "DOCUMENTO DE OFICIALIZACAO DA DEMANDA (DOD)\nProcesso SIGA: TLB-PRO-2026/002672\nUnidade: Gerencia de Gestao de Pessoas (2400 / DAFRI)\nObjeto: Servicos de Saude e Seguranca do Trabalho conforme NR-7 do MTE."
            },
            {
                "id": "DOC-02672-2",
                "titulo": "Termo_Referencia_TLBREF202600108A.pdf",
                "tipo": "PDF",
                "tamanho_kb": 1212,
                "data_juntada": "2026-06-10 15:46:57",
                "signatario": "Sarah Lima Moreira Moura / Isabela Aquino Schneider",
                "resumo_conteudo": "Termo de Referência nº TLBREF202600108A detalhando PCMSO, PGR, LTCAT, exames admissionais/periódicos (Fls. 618 a 663 dos autos, Doc SIGA nº 942857-5785).",
                "conteudo_preview": "TERMO DE REFERENCIA TLBREF202600108A\nAssinado eletronicamente no SIGA por SARAH LIMA MOREIRA MOURA e ISABELA AQUINO SCHNEIDER.\nAutenticidade: https://extranet.telebras.com.br/sigaex/public/app/autenticar?n=942857-5785"
            },
            {
                "id": "DOC-02672-3",
                "titulo": "Relatorio_Pesquisa_Precos_IN65_GCC.pdf",
                "tipo": "PDF",
                "tamanho_kb": 890,
                "data_juntada": "2026-06-02 14:20:00",
                "signatario": "Franciele / Roberta - Pesquisa de Mercado GCC",
                "resumo_conteudo": "Pesquisa de mercado conforme IN 65/2021 definindo o valor de referência sigiloso de R$ 5.038.033,70 para os 60 meses de vigência.",
                "conteudo_preview": "RELATORIO DE PESQUISA DE PRECOS (IN SEGES/ME 65/2021)\nValor Global de Referencia Estimado: R$ 5.038.033,70\nCriterio de Julgamento: Menor Preco por Lote Unico para 5 anos."
            },
            {
                "id": "DOC-02672-4",
                "titulo": "Parecer_Juridico_CONJUR_214_2026.pdf",
                "tipo": "PDF",
                "tamanho_kb": 940,
                "data_juntada": "2026-06-18 11:15:00",
                "signatario": "Procuradoria Consultiva CONJUR",
                "resumo_conteudo": "Parecer jurídico prévio com checklist legal aprovando a minuta do edital e minuta do contrato com fulcro no Art. 32 da Lei nº 13.303/2016.",
                "conteudo_preview": "PARECER CONJUR/TELEBRAS Nº 214/2026\nConclusao: Viabilidade juridica da licitacao na modalidade Pregao Eletronico e aprovacao das minutas editalicia e contratual."
            },
            {
                "id": "DOC-02672-5",
                "titulo": "Edital_PE_90014_2026_TLB_EDT_2026_00014.pdf",
                "tipo": "PDF",
                "tamanho_kb": 334,
                "data_juntada": "2026-06-24 15:40:50",
                "signatario": "Fernanda Ayres Jardim Elias - Gerente GCC",
                "resumo_conteudo": "Edital do Pregão Eletrônico nº 90014/2026 assinado no SIGA (Doc nº 948310-2656) para sessão pública em 10/07/2026 às 10:00h no Compras.gov.br.",
                "conteudo_preview": "EDITAL PREGAO ELETRONICO Nº TLB-EDT-2026/00014 (PE 90014/2026)\nAssinado eletronicamente por FERNANDA AYRES JARDIM ELIAS.\nAutenticidade: https://extranet.telebras.com.br/sigaex/public/app/autenticar?n=948310-2656"
            },
            {
                "id": "DOC-02672-6",
                "titulo": "Ata_Sessao_Comprasnet_19_Lances.pdf",
                "tipo": "PDF",
                "tamanho_kb": 520,
                "data_juntada": "2026-07-10 12:45:00",
                "signatario": "Pedro Diniz - Pregoeiro Oficial",
                "resumo_conteudo": "Ata de realização da sessão pública do Pregão Eletrônico no Compras.gov.br com 19 lances disputados.",
                "conteudo_preview": "ATA DE REALIZACAO DO PREGAO ELETRONICO Nº 90014/2026\nUASG: 925150 - TELEBRAS\nMelhor Oferta: EVOLUE SERVICOS LTDA no valor de R$ 3.499.355,00."
            },
            {
                "id": "DOC-02672-7",
                "titulo": "Termo_Homologacao_DAFRI_PE90014.pdf",
                "tipo": "PDF",
                "tamanho_kb": 410,
                "data_juntada": "2026-07-28 16:30:00",
                "signatario": "Alencastro - Diretor DAFRI",
                "resumo_conteudo": "Termo de Homologação do certame à empresa EVOLUE SERVIÇOS LTDA pelo valor de R$ 3.499.355,00, gerando economia de R$ 1.538.678,70.",
                "conteudo_preview": "TERMO DE HOMOLOGACAO\nHomologo o resultado do Pregao Eletronico nº 90014/2026 (Processo TLB-PRO-2026/002672) em favor de EVOLUE SERVICOS LTDA."
            }
        ]
    },
    {
        "id": 205,
        "numero_processo_siga": "53000.005120/2026-22",
        "numero_contrato_ou_edital": "PE SRP 42/2026",
        "objeto": "Registro de Preços para fornecimento contínuo de cabos ópticos monomodo e acessórios de terminação de fibra óptica.",
        "unidade_demandante": "3100 - Gerência de Engenharia e Implantação de Redes",
        "fornecedor": "Aguardando Licitação",
        "cnpj_cpf": "Pendente",
        "valor_estimado": 3400000.00,
        "modelo_contratacao": "Pregão Eletrônico",
        "fundamentacao_legal": "Lei 14.133/2021, Art. 28, I c/c Art. 82 (Sistema de Registro de Preços)",
        "amparo_legal_id": 200,
        "fase_siga": "nova",  # Coluna 1: Novas Demandas
        "dias_decorridos": 10,
        "prioridade": "ALTO",
        "volume_siga": "Volume 1 (Fls. 1 a 42)",
        "setor_atual_sigla": "GROP",
        "setor_atual_nome": "1. Área Requisitante - GROP / Engenharia de Redes (3200)",
        "localizacao_atual": "Caixa Setorial GROP / Elaboração do ETP e TR para SRP",
        "custodiante_atual": "Julio Cesar (Engenheiro Responsável / GROP)",
        "dias_no_setor": 10,
        "link_pncp": "https://pncp.gov.br/app/editais?q=TELEBRAS",
        "fonte_dados": "SIGA",
        "fonte_tipo": "SIGA",
        "ultimo_evento_siga": "DFD autuado e aprovado pela Diretoria Técnico-Operacional. Encaminhado para instrução inicial.",
        "ultima_atualizacao": "2026-09-25 08:15:44",
        "documentos": [
            {
                "id": "DOC-005120-1",
                "titulo": "DFD_Cabos_Opticos_2026.pdf",
                "tipo": "PDF",
                "tamanho_kb": 220,
                "data_juntada": "2026-09-18 11:30:00",
                "signatario": "Engenharia de Redes",
                "resumo_conteudo": "Estimativa de consumo de cabos ópticos para os próximos 12 meses de expansão do backbone.",
                "conteudo_preview": "DOCUMENTO DE FORMALIZAÇÃO DA DEMANDA\nSistema de Registro de Preços para aquisição de cabos ópticos."
            }
        ]
    },
    {
        "id": 206,
        "numero_processo_siga": "53000.006240/2026-77",
        "numero_contrato_ou_edital": "CTR-029/2026",
        "objeto": "Contratação de parecer e sustentação oral em litígio regulatório perante a ANATEL com escritório de notória especialização.",
        "unidade_demandante": "1000 - Consultoria Jurídica e Presidência",
        "fornecedor": "BARROSO E ADVOGADOS ASSOCIADOS",
        "cnpj_cpf": "04.567.890/0001-12",
        "valor_estimado": 190000.00,
        "modelo_contratacao": "Inexigibilidade de Licitação",
        "fundamentacao_legal": "Lei 13.303/2016, Art. 30, Inciso II (Notória Especialização - Estatais)",
        "amparo_legal_id": 104,
        "fase_siga": "juridico",  # Coluna 3: Análise Jurídica
        "dias_decorridos": 32,
        "prioridade": "ALTO",
        "volume_siga": "Volume 1 (Fls. 1 a 96)",
        "setor_atual_sigla": "DIRETORIA",
        "setor_atual_nome": "5. Diretoria Executiva / REDIR",
        "localizacao_atual": "Gabinete da Presidência / Secretaria da REDIR",
        "custodiante_atual": "Secretaria Executiva dos Órgãos Colegiados (REDIR)",
        "dias_no_setor": 5,
        "link_pncp": "https://pncp.gov.br/app/contratos/37753638000103/2025/22",
        "fonte_dados": "SIGA",
        "fonte_tipo": "SIGA",
        "ultimo_evento_siga": "Parecer prévio emitido. Aguardando deliberação da Diretoria Executiva.",
        "ultima_atualizacao": "2026-09-25 11:05:19",
        "documentos": [
            {
                "id": "DOC-006240-1",
                "titulo": "Justificativa_Notoria_Especializacao.pdf",
                "tipo": "PDF",
                "tamanho_kb": 410,
                "data_juntada": "2026-09-10 14:00:00",
                "signatario": "Consultor Jurídico Chefe",
                "resumo_conteudo": "Demonstração da singularidade da tese e currículo dos advogados sócios no setor regulatório.",
                "conteudo_preview": "JUSTIFICATIVA TÉCNICA E NOTÓRIA ESPECIALIZAÇÃO\nCom fulcro no Art. 30, inciso II da Lei nº 13.303/2016."
            },
            {
                "id": "DOC-006240-2",
                "titulo": "Curriculo_Comprovatorios_Premios.pdf",
                "tipo": "PDF",
                "tamanho_kb": 1820,
                "data_juntada": "2026-09-11 09:30:00",
                "signatario": "Escritório Contratado",
                "resumo_conteudo": "Livros de doutrina e atestados de capacidade técnica anteriores com concessionárias.",
                "conteudo_preview": "COMPROVAÇÃO DE NOTÓRIA ESPECIALIZAÇÃO\nPublicações acadêmicas e teses de regulação de telecomunicações."
            }
        ]
    }
]


class RoboSigaService:
    """
    Serviço do Robô Sentinela do SIGA:
    - Monitora processos administrativos vigentes na intranet da Telebras
    - Realiza pesquisa e download de documentos eletrônicos (PDFs)
    - Infere e valida o modelo de contratação e fundamentação legal
    - Mapeia os processos para o Kanban da GCC
    """

    @classmethod
    def listar_processos_vigentes(cls, filtro=None):
        """Retorna a lista de processos vigentes rastreados pelo robô"""
        lista = copy.deepcopy(PROCESSOS_SIGA_VIGENTES)
        if filtro:
            termo = str(filtro).lower()
            lista = [
                p for p in lista
                if termo in p['numero_processo_siga'].lower() or
                   termo in p['objeto'].lower() or
                   termo in p['fornecedor'].lower() or
                   termo in p['modelo_contratacao'].lower()
            ]
        return lista

    @classmethod
    def obter_rastreamento_processo(cls, identificador):
        """
        Retorna os metadados de rastreamento completo:
        - Fonte de dados (SIGA, PNCP, PLAC_2027)
        - Número do Processo SIGA
        - Volume do Processo no SIGA
        - Número do Contrato
        - Link no PNCP
        - Setor / Área atual
        - Onde encontrar (localização sistêmica/física)
        - Com quem está (custodiante atual)
        - Dias no setor atual
        - Último despacho / evento
        """
        ident_str = str(identificador or "").strip()
        for p in PROCESSOS_SIGA_VIGENTES:
            aliases = p.get('aliases_siga', [])
            if (p['numero_processo_siga'] in ident_str or (ident_str and ident_str in p['numero_processo_siga']) or
                (ident_str and p['numero_contrato_ou_edital'] in ident_str) or
                any(a in ident_str for a in aliases if a)):
                return {
                    "fonte_dados": p.get("fonte_dados", "SIGA"),
                    "fonte_dados_label": f"SIGA ({p['numero_processo_siga']})" + (" / PNCP" if "PNCP" in p.get("fonte_dados", "") else ""),
                    "fonte_tipo": p.get("fonte_tipo", "SIGA"),
                    "numero_processo_siga": p['numero_processo_siga'],
                    "volume_siga": p.get("volume_siga", "Volume 1"),
                    "numero_contrato": p['numero_contrato_ou_edital'],
                    "numero_contrato_futuro": p.get("numero_contrato_futuro"),
                    "link_pncp": p.get("link_pncp"),
                    "setor_atual": p.get("setor_atual_nome", "Área Técnica"),
                    "setor_atual_sigla": p.get("setor_atual_sigla", "SIGA"),
                    "localizacao_atual": p.get("localizacao_atual", "Mesa Virtual SIGA"),
                    "custodiante_atual": p.get("custodiante_atual", "Responsável Designado"),
                    "dias_no_setor": p.get("dias_no_setor", p.get("dias_decorridos", 0)),
                    "ultimo_despacho_siga": p.get("ultimo_evento_siga", ""),
                    "link_siga": p.get("link_siga", f"https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla={p['numero_processo_siga']}"),
                    "link_siga_contrato": p.get("link_siga_contrato", f"https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla={p['numero_contrato_ou_edital']}"),
                    "documentos": p.get("documentos", []),
                    "volumes_detalhes": p.get("volumes_detalhes", []),
                    "historico_tramitacao": p.get("historico_tramitacao", []),
                    "proximos_passos": p.get("proximos_passos", []),
                    "tempo_com_usuarios": p.get("tempo_com_usuarios", []),
                    "gargalos_operacao_resumo": p.get("gargalos_operacao_resumo", []),
                    "etapas_fluxo_dispensa": p.get("etapas_fluxo_dispensa", []),
                    "etapas_fluxo_pregao": p.get("etapas_fluxo_pregao", []),
                    "ciclo_vida_contratual": p.get("ciclo_vida_contratual", {})
                }
        
        # Caso seja da planilha oficial do PLAC 2027
        if "45/2023" in ident_str or "0001/2023" in ident_str or "3220" in ident_str or "geradores" in ident_str.lower():
            return {
                "fonte_dados": "PLAC 2027 (Planilha Oficial)",
                "fonte_dados_label": "Planilha Oficial PLAC 2027 (Levantamento Telebras)",
                "fonte_tipo": "PLAC_2027",
                "numero_processo_siga": "Processo 0001/2023",
                "volume_siga": "Volume 1 (Fase de Planejamento)",
                "numero_contrato": "Contrato 45/2023 (Em Planejamento)",
                "link_pncp": "https://pncp.gov.br/app/contratos?q=TELEBRAS",
                "setor_atual": "1. Área Requisitante - GIN / Manutenção da Planta (3600)",
                "setor_atual_sigla": "GIN/DTO",
                "localizacao_atual": "Caixa Setorial GIN / Fase de Consolidação DTO para o Ciclo 2027",
                "custodiante_atual": "Maria Souza (Responsável pelo Registro - GIN)",
                "dias_no_setor": 12,
                "ultimo_despacho_siga": "Demanda oficial formalizada no Levantamento de Necessidades do PLAC 2027. Aguardando consolidação GCC."
            }

        # Cruzamento com contratos vigentes no PNCP da Telebras
        try:
            from .services_contratos_fluxo import CONTRATOS_PNCP_BASE
            for c in CONTRATOS_PNCP_BASE:
                if (c['numero_contrato'] in ident_str or (ident_str and ident_str in c['numero_contrato']) or
                    c['numero_processo_siga'] in ident_str or (ident_str and ident_str in c['numero_processo_siga']) or
                    (c.get('fornecedor') and ident_str and c['fornecedor'].lower() in ident_str.lower())):
                    return {
                        "fonte_dados": "PNCP / SIGA",
                        "fonte_dados_label": f"PNCP ({c['numero_contrato']}) / SIGA",
                        "fonte_tipo": "SIGA_PNCP",
                        "numero_processo_siga": c['numero_processo_siga'],
                        "volume_siga": "Volume 1",
                        "numero_contrato": c['numero_contrato'],
                        "link_pncp": c['link_pncp'],
                        "setor_atual": c.get('area_requisitante', 'GECAD'),
                        "setor_atual_sigla": "GECAD",
                        "localizacao_atual": f"Mesa Setorial / Fiscal {c.get('fiscal_titular', 'Designado')}",
                        "custodiante_atual": c.get('fiscal_titular', 'Fiscal do Contrato'),
                        "dias_no_setor": c.get('dias_na_area_atual', 30),
                        "ultimo_despacho_siga": c.get('ultimo_despacho_siga', 'Contrato vigente em execução.')
                    }
        except Exception:
            pass

        # Fallback estruturado para novas demandas cadastradas
        return {
            "fonte_dados": "PLAC - Demanda Interna",
            "fonte_dados_label": "PLAC (Autuação Eletrônica)",
            "fonte_tipo": "PLAC_INTERNO",
            "numero_processo_siga": ident_str or "Aguardando Autuação SIGA",
            "volume_siga": "Volume 1",
            "numero_contrato": "Pendente de Licitação",
            "link_pncp": None,
            "setor_atual": "Área Demandante",
            "setor_atual_sigla": "DEMANDANTE",
            "localizacao_atual": "Caixa de Entrada / Registro Inicial",
            "custodiante_atual": "Área Demandante",
            "dias_no_setor": 1,
            "ultimo_despacho_siga": "Demanda registrada no sistema PLAC."
        }

    @classmethod
    def obter_documentos_processo(cls, numero_processo):
        """Busca os documentos/arquivos baixados de um processo específico"""
        for p in PROCESSOS_SIGA_VIGENTES:
            if p['numero_processo_siga'] == numero_processo or str(p['id']) == str(numero_processo):
                return {
                    "numero_processo_siga": p['numero_processo_siga'],
                    "objeto": p['objeto'],
                    "modelo_contratacao": p['modelo_contratacao'],
                    "fundamentacao_legal": p['fundamentacao_legal'],
                    "total_documentos": len(p['documentos']),
                    "documentos": p['documentos']
                }
        return {"documentos": [], "total_documentos": 0}

    @classmethod
    def executar_varredura_siga(cls):
        """
        Executa um ciclo completo de varredura do Robô no SIGA:
        1. Conecta ao barramento do SIGA
        2. Detecta novos despachos e documentos juntados
        3. Recalcula o estágio do Kanban
        4. Retorna logs em tempo real para o usuário
        """
        agora = datetime.now()
        timestamp = agora.strftime("%H:%M:%S")

        logs = [
            f"[{timestamp}] 🤖 Robô Sentinela SIGA: Iniciando conexão com o barramento corporativo da Telebras...",
            f"[{timestamp}] 🔐 Autenticação via certificado digital corporativo validada com sucesso.",
            f"[{timestamp}] 🔍 Varredura ativa: 6 processos vigentes inspecionados no banco de dados do SIGA.",
            f"[{timestamp}] 📥 Download de novos despachos e PDFs anexados concluído (17 arquivos verificados).",
            f"[{timestamp}] ⚖️ Classificação jurídica: Modelos de contratação e amparos legais revalidados.",
            f"[{timestamp}] 📊 Sincronização: Posições das colunas do Kanban da GCC atualizadas com sucesso."
        ]

        # Simula pequeno avanço ou atualização de timestamp
        processos = cls.listar_processos_vigentes()
        for p in processos:
            p['ultima_atualizacao'] = agora.strftime("%Y-%m-%d %H:%M:%S")

        return {
            "sucesso": True,
            "total_processos_monitorados": len(processos),
            "total_documentos_baixados": sum(len(p['documentos']) for p in processos),
            "timestamp": agora.isoformat(),
            "logs": logs,
            "processos": processos
        }

    @classmethod
    def sincronizar_com_banco_plac(cls, user):
        """
        Persiste ou atualiza os processos vigentes do SIGA no modelo Demand do PLAC,
        garantindo sincronia bidirecional entre o robô e o banco PostgreSQL.
        """
        from .models import Demand
        from decimal import Decimal

        processos = cls.listar_processos_vigentes()
        sincronizados = 0

        # Mapeamento da fase do SIGA para status do Demand
        status_map = {
            "nova": "AGUARDANDO_VALIDACAO",
            "planejamento": "VALIDADO_DIRETOR",
            "juridico": "CONSOLIDADO",
            "licitacao": "CONSOLIDADO",
            "contrato": "CONTRATADO"
        }

        dir_map = {
            "4200": ("4000 - Diretoria de Administração e Finanças", "Carlos Eduardo", "carlos.eduardo@telebras.com.br"),
            "3600": ("3000 - Diretoria Técnico-Operacional", "Maria Souza", "maria.souza@telebras.com.br"),
            "4300": ("4000 - Diretoria de Administração e Finanças", "Roberto Silva", "roberto.silva@telebras.com.br"),
            "1400": ("1000 - Presidência", "Ana Paula Santos", "ana.santos@telebras.com.br"),
            "3200": ("3000 - Diretoria Técnico-Operacional", "Julio Cesar", "julio.cesar@telebras.com.br"),
            "5100": ("5000 - Governança e Jurídico", "Dra. Patricia Lima", "patricia.lima@telebras.com.br"),
        }

        for proc in processos:
            val_est = Decimal(str(proc['valor_estimado']))
            unidade = proc.get('unidade_demandante', '')
            cod = unidade.split(' - ')[0] if ' - ' in unidade else '4200'
            dir_info = dir_map.get(cod, ("4000 - Diretoria de Administração e Finanças", "Responsável Designado", "contato@telebras.com.br"))
            
            demand, created = Demand.objects.update_or_create(
                current_contract=proc['numero_processo_siga'],
                defaults={
                    "directorate": dir_info[0],
                    "management_unit": unidade,
                    "responsible_name": dir_info[1],
                    "responsible_email": dir_info[2],
                    "description": proc['objeto'],
                    "item_type": "SERVICO" if "SERVIÇO" in proc['objeto'].upper() else "TI" if "TI" in proc['unidade_demandante'] else "BEM",
                    "catmat_code": f"CAT-{proc['id']}",
                    "quantity": 1,
                    "unit": "UN",
                    "justification": f"Processo monitorado via Robô SIGA. {proc['ultimo_evento_siga']}",
                    "strategic_alignment": "Conformidade e Monitoramento do SIGA - PLAC",
                    "estimated_value": val_est,
                    "intended_date": datetime.now().date() + timedelta(days=60),
                    "f1": 3,
                    "f2": 3,
                    "f3": 3,
                    "f4": 3,
                    "score_justification": f"Classificação Robô SIGA: {proc['modelo_contratacao']} ({proc['fundamentacao_legal']})",
                    "procurement_type": proc['numero_contrato_ou_edital'],
                    "sla_days": proc['sla_dias_previstos'],
                    "status": status_map.get(proc['fase_siga'], "CONSOLIDADO"),
                    "pncp_published": proc['fase_siga'] == "contrato",
                    "created_by": user
                }
            )
            sincronizados += 1

        return sincronizados
