from datetime import datetime, timedelta
import re

# Catálogo consolidado dos Amparos Legais oficiais do PNCP para Lei 14.133/2021 e Lei 13.303/2016
AMPAROS_PNCP = [
    # --- LEI 14.133/2021 - INEXIGIBILIDADE (Modalidade ID 9) ---
    {
        "id": 51,
        "modalidade_id": 9,
        "lei": "14.133/2021",
        "artigo": "74",
        "inciso": "I",
        "nome": "Lei 14.133/2021, Art. 74, Inciso I - Fornecedor Exclusivo",
        "descricao": "Aquisição de materiais, de equipamentos ou de gêneros ou contratação de serviços que só possam ser fornecidos por produtor, empresa ou representante comercial exclusivo.",
        "requisitos_tcu": "Atestado de exclusividade emitido por sindicato, federação ou entidade competente; comprovação de inviabilidade de competição; pesquisa de preços com órgãos contratantes anteriores.",
        "risco_tcu": "ALTO se não houver certidão oficial de exclusividade válida."
    },
    {
        "id": 52,
        "modalidade_id": 9,
        "lei": "14.133/2021",
        "artigo": "74",
        "inciso": "II",
        "nome": "Lei 14.133/2021, Art. 74, Inciso II - Notória Especialização (Serviços Intelectuais)",
        "descricao": "Contratação de serviços técnicos especializados de natureza predominantemente intelectual com profissionais ou empresas de notória especialização (vedada para publicidade e divulgação).",
        "requisitos_tcu": "Comprovação da singularidade do serviço e da notoriedade inconteste do contratado (currículos, prêmios, livros publicados, casos de sucesso anteriores).",
        "risco_tcu": "MÉDIO. Exige justificativa formal de inviabilidade de competição e singularidade do objeto."
    },
    {
        "id": 53,
        "modalidade_id": 9,
        "lei": "14.133/2021",
        "artigo": "74",
        "inciso": "III",
        "nome": "Lei 14.133/2021, Art. 74, Inciso III - Setor Artístico",
        "descricao": "Contratação de profissional do setor artístico, diretamente ou por meio de empresário exclusivo, desde que consagrado pela crítica especializada ou pela opinião pública.",
        "requisitos_tcu": "Empresário exclusivo legítimo com contrato registrado ou representação direta; comprovação de consagração pública/crítica.",
        "risco_tcu": "MÉDIO. Atenção à comprovação de empresário exclusivo e preço de mercado."
    },
    {
        "id": 54,
        "modalidade_id": 9,
        "lei": "14.133/2021",
        "artigo": "74",
        "inciso": "IV",
        "nome": "Lei 14.133/2021, Art. 74, Inciso IV - Objetos via Credenciamento",
        "descricao": "Contratação de serviços ou bens que devam ou possam ser contratados por meio de credenciamento.",
        "requisitos_tcu": "Edital permanente de credenciamento publicado previamente; tratamento isonômico a todos os credenciados.",
        "risco_tcu": "BAIXO se cumprido o rito do Art. 79."
    },
    {
        "id": 55,
        "modalidade_id": 9,
        "lei": "14.133/2021",
        "artigo": "74",
        "inciso": "V",
        "nome": "Lei 14.133/2021, Art. 74, Inciso V - Imóvel com características singulares",
        "descricao": "Aquisição ou locação de imóvel cujas características de instalações e de localização tornem necessária sua escolha.",
        "requisitos_tcu": "Estudo prévio de avaliação mercadológica e justificativa técnica das razões de localização e instalações.",
        "risco_tcu": "MÉDIO. Requer laudo de avaliação por profissional habilitado."
    },

    # --- LEI 14.133/2021 - DISPENSA (Modalidade ID 8) ---
    {
        "id": 61,
        "modalidade_id": 8,
        "lei": "14.133/2021",
        "artigo": "75",
        "inciso": "I",
        "nome": "Lei 14.133/2021, Art. 75, Inciso I - Limite de Valor (Obras e Serviços de Engenharia)",
        "descricao": "Contratação de obras e serviços de engenharia ou de serviços de manutenção de veículos automotores até o limite legal (R$ 119.812,02).",
        "requisitos_tcu": "Controle rígido contra fracionamento de despesa no exercício corrente; pesquisa prévia de preços com no mínimo 3 orçamentos (Art. 23).",
        "risco_tcu": "MÉDIO. Atenção ao somatório de despesas da mesma natureza pela mesma unidade gestora."
    },
    {
        "id": 62,
        "modalidade_id": 8,
        "lei": "14.133/2021",
        "artigo": "75",
        "inciso": "II",
        "nome": "Lei 14.133/2021, Art. 75, Inciso II - Limite de Valor (Outros Serviços e Compras)",
        "descricao": "Contratação de outros serviços e compras até o limite legal (R$ 59.906,02).",
        "requisitos_tcu": "Controle de fracionamento de despesa (Art. 75, § 1º); pesquisa de preços em bases públicas (Painel de Preços, PNCP, compras públicas).",
        "risco_tcu": "MÉDIO. Risco principal é o fracionamento indevido de compras semelhantes."
    },
    {
        "id": 68,
        "modalidade_id": 8,
        "lei": "14.133/2021",
        "artigo": "75",
        "inciso": "VIII",
        "nome": "Lei 14.133/2021, Art. 75, Inciso VIII - Emergência ou Calamidade Pública",
        "descricao": "Nos casos de emergência ou de calamidade pública, para atendimento indispensável e pelo prazo estritamente necessário (máx. 1 ano).",
        "requisitos_tcu": "Demonstração inequívoca da urgência, do risco de dano irreparável e de que a contratação se limita à parcela necessária para afastar o perigo.",
        "risco_tcu": "ALTO. O TCU pune severamente a 'emergência fabricada' por desídia administrativa."
    },
    {
        "id": 69,
        "modalidade_id": 8,
        "lei": "14.133/2021",
        "artigo": "75",
        "inciso": "IX",
        "nome": "Lei 14.133/2021, Art. 75, Inciso IX - Pesquisa, Desenvolvimento e Inovação (PD&I)",
        "descricao": "Para a aquisição ou contratação de produto para pesquisa e desenvolvimento.",
        "requisitos_tcu": "Projeto de pesquisa aprovado e justificativa de correlação com as finalidades institucionais.",
        "risco_tcu": "BAIXO a MÉDIO."
    },

    # --- LEI 14.133/2021 - CREDENCIAMENTO (Modalidade ID 10) ---
    {
        "id": 79,
        "modalidade_id": 10,
        "lei": "14.133/2021",
        "artigo": "79",
        "inciso": "I",
        "nome": "Lei 14.133/2021, Art. 79, Inciso I - Credenciamento Paralelo e Não Excludente",
        "descricao": "Credenciamento em que é viável e vantajosa para a Administração a contratação simultânea de todos os habilitados em condições padronizadas (ex: serviços médicos, peritos, leiloeiros).",
        "requisitos_tcu": "Edital aberto o ano todo; remuneração previamente fixada pelo órgão; regras objetivas de distribuição ou escolha do usuário.",
        "risco_tcu": "BAIXO. Modelo amplamente aceito para expansão de rede credenciada."
    },
    {
        "id": 80,
        "modalidade_id": 10,
        "lei": "14.133/2021",
        "artigo": "79",
        "inciso": "II",
        "nome": "Lei 14.133/2021, Art. 79, Inciso II - Seleção a Critério de Terceiros",
        "descricao": "Credenciamento com seleção a critério do beneficiário direto (ex: passagens, clínicas conveniadas, vale-alimentação).",
        "requisitos_tcu": "Liberdade irrestrita de escolha do usuário final dentre os previamente credenciados.",
        "risco_tcu": "BAIXO."
    },

    # --- LEI 13.303/2016 (LEI DAS ESTATAIS - TELEBRAS) ---
    {
        "id": 101,
        "modalidade_id": 8,
        "lei": "13.303/2016",
        "artigo": "29",
        "inciso": "I",
        "nome": "Lei 13.303/2016, Art. 29, Inciso I - Limite de Valor Obras e Engenharia",
        "descricao": "Dispensa para obras e serviços de engenharia até o valor legal atualizado (R$ 119.812,02).",
        "requisitos_tcu": "Pesquisa de preços conforme regulamento interno da estatal; controle de fracionamento.",
        "risco_tcu": "MÉDIO."
    },
    {
        "id": 102,
        "modalidade_id": 8,
        "lei": "13.303/2016",
        "artigo": "29",
        "inciso": "II",
        "nome": "Lei 13.303/2016, Art. 29, Inciso II - Limite de Valor Outros Serviços e Compras",
        "descricao": "Dispensa para outros serviços e compras de valor até o limite legal (R$ 59.906,02).",
        "requisitos_tcu": "Verificação do planejamento anual de contratações para evitar fracionamento.",
        "risco_tcu": "MÉDIO."
    },
    {
        "id": 103,
        "modalidade_id": 9,
        "lei": "13.303/2016",
        "artigo": "30",
        "inciso": "I",
        "nome": "Lei 13.303/2016, Art. 30, Inciso I - Fornecedor Exclusivo (Estatais)",
        "descricao": "Inexigibilidade para aquisição de materiais, equipamentos ou gêneros que só possam ser fornecidos por produtor, empresa ou representante comercial exclusivo.",
        "requisitos_tcu": "Atestado emitido por órgão de registro do comércio ou sindicato da indústria/comércio; justificativa de preço.",
        "risco_tcu": "ALTO se houver produtos concorrentes com viabilidade de atendimento."
    },
    {
        "id": 104,
        "modalidade_id": 9,
        "lei": "13.303/2016",
        "artigo": "30",
        "inciso": "II",
        "nome": "Lei 13.303/2016, Art. 30, Inciso II - Notória Especialização (Estatais)",
        "descricao": "Inexigibilidade para contratação de serviços técnicos especializados com profissionais ou empresas de notória especialização.",
        "requisitos_tcu": "Demonstração da singularidade e adequação do perfil técnico notório.",
        "risco_tcu": "MÉDIO."
    },

    # --- PREGÃO ELETRÔNICO (Modalidade ID 6) ---
    {
        "id": 200,
        "modalidade_id": 6,
        "lei": "14.133/2021",
        "artigo": "28",
        "inciso": "I",
        "nome": "Lei 14.133/2021, Art. 28, Inciso I - Pregão Eletrônico (Bens e Serviços Comuns)",
        "descricao": "Modalidade de licitação obrigatória para aquisição de bens e serviços comuns, cujo critério de julgamento poderá ser o de menor preço ou de maior desconto.",
        "requisitos_tcu": "Pesquisa ampla de mercado com mínimo de 3 orçamentos idôneos; ETP detalhado; edital e matriz de riscos padronizados.",
        "risco_tcu": "BAIXO (modalidade padrão e preferencial de ampla disputa)."
    }
]


def listar_amparos(modalidade_id=None, lei_filtro=None):
    """Retorna lista de amparos filtrados"""
    resultado = AMPAROS_PNCP
    if modalidade_id:
        resultado = [a for a in resultado if a['modalidade_id'] == int(modalidade_id)]
    if lei_filtro:
        resultado = [a for a in resultado if lei_filtro in a['lei']]
    return resultado


def julgar_enquadramento_legal(dados_entrada):
    """
    Motor do Tribunal da IA:
    Avalia a pretensão de compra da área demandante e emite:
    1. Veredito do Juiz Relator (Modalidade, Fundamentação, Amparo PNCP e Tese)
    2. Parecer do Auditor de Riscos TCU (Score, Alertas de Fracionamento, Súmulas e Checklist)
    3. Minuta Técnica da Compra (Objeto lapidado, Justificativa, Vigência, Itens Sugeridos)
    """
    objeto_raw = str(dados_entrada.get('objeto', '')).strip()
    valor_estimado = float(dados_entrada.get('valor_estimado', 0.0) or 0.0)
    regime_lei = str(dados_entrada.get('regime_lei', '14.133/2021')).strip()
    is_estatal = '13.303' in regime_lei
    
    tipo_objeto = str(dados_entrada.get('tipo_objeto', 'SERVICO')).upper()
    is_exclusivo = bool(dados_entrada.get('is_exclusivo', False))
    is_notoria_especializacao = bool(dados_entrada.get('is_notoria_especializacao', False))
    is_credenciamento = bool(dados_entrada.get('is_credenciamento', False))
    is_emergencial = bool(dados_entrada.get('is_emergencial', False))
    is_continuo = bool(dados_entrada.get('is_continuo', True if tipo_objeto == 'SERVICO' else False))
    
    # ── 1. JULGAMENTO DE MÉRITO (JUIZ RELATOR) ──
    modalidade_id = 6  # Default: Pregão Eletrônico
    modalidade_nome = "Pregão Eletrônico"
    amparo_escolhido = None
    tese_juridica = ""
    
    # Análise de texto para capturar pistas caso os checkboxes não tenham sido marcados
    txt_lower = objeto_raw.lower()
    if any(k in txt_lower for k in ['exclusiv', 'único fornecedor', 'fabricante exclusivo', 'monopólio']):
        is_exclusivo = True
    if any(k in txt_lower for k in ['notória especialização', 'notorio especialista', 'jurista', 'consultoria singular', 'renomado']):
        is_notoria_especializacao = True
    if any(k in txt_lower for k in ['credenciamento', 'rede credenciada', 'clínicas credenciadas', 'peritos credenciados']):
        is_credenciamento = True
    if any(k in txt_lower for k in ['emergênc', 'calamidade', 'risco iminente', 'desabamento', 'pane crítica']):
        is_emergencial = True

    # Limites legais de valor
    teto_dispensa_engenharia = 119812.02
    teto_dispensa_compras = 59906.02
    limite_dispensa_aplicavel = teto_dispensa_engenharia if 'OBRA' in tipo_objeto or 'ENGENHARIA' in tipo_objeto else teto_dispensa_compras

    if is_emergencial:
        modalidade_id = 8
        modalidade_nome = "Dispensa de Licitação (Emergência)"
        if is_estatal:
            amparo_escolhido = next((a for a in AMPAROS_PNCP if a['lei'] == '13.303/2016' and a['artigo'] == '29' and 'XV' in a.get('inciso', '')), None)
            if not amparo_escolhido:
                amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 102), None)
            tese_juridica = "Enquadramento com fulcro no Art. 29 da Lei 13.303/2016 diante da caracterização de situação emergencial inadiável que compromete a operação da estatal."
        else:
            amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 68), None)
            tese_juridica = "Enquadramento no Art. 75, inciso VIII da Lei 14.133/2021. Configurada a necessidade premente de atendimento de situação emergencial ou calamitosa para afastar risco à segurança ou aos serviços públicos."
            
    elif is_credenciamento:
        modalidade_id = 10
        modalidade_nome = "Credenciamento"
        amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 79), None)
        tese_juridica = "Enquadramento como procedimento auxiliar de Credenciamento (Art. 79, inciso I da Lei nº 14.133/2021). A Administração visa a contratação simultânea e paralela de todos os prestadores aptos sob edital aberto permanente."

    elif is_exclusivo:
        modalidade_id = 9
        modalidade_nome = "Inexigibilidade de Licitação (Fornecedor Exclusivo)"
        if is_estatal:
            amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 103), None)
            tese_juridica = "Enquadramento no Art. 30, inciso I da Lei nº 13.303/2016. Inviabilidade de competição comprovada decorrente da exclusividade de fornecimento atestada por órgão competente."
        else:
            amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 51), None)
            tese_juridica = "Enquadramento no Art. 74, inciso I da Lei nº 14.133/2021. Inviabilidade de competição decorrente de fornecedor exclusivo, vedada a preferência de marca injustificada."

    elif is_notoria_especializacao:
        modalidade_id = 9
        modalidade_nome = "Inexigibilidade de Licitação (Notória Especialização)"
        if is_estatal:
            amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 104), None)
            tese_juridica = "Enquadramento no Art. 30, inciso II da Lei nº 13.303/2016. Contratação direta de serviço técnico especializado de natureza intelectual com profissional/empresa de notoriedade inconteste."
        else:
            amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 52), None)
            tese_juridica = "Enquadramento no Art. 74, inciso II da Lei nº 14.133/2021. Configurada a singularidade do serviço e a notória especialização do contratado para entrega de prestação predominantemente intelectual."

    elif valor_estimado > 0 and valor_estimado <= limite_dispensa_aplicavel:
        modalidade_id = 8
        modalidade_nome = "Dispensa de Licitação (Limite de Valor)"
        if is_estatal:
            if 'OBRA' in tipo_objeto or 'ENGENHARIA' in tipo_objeto:
                amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 101), None)
            else:
                amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 102), None)
            tese_juridica = f"Enquadramento no Art. 29, inciso II da Lei nº 13.303/2016. O valor orçado (R$ {valor_estimado:,.2f}) encontra-se estritamente abaixo do teto legal de dispensa."
        else:
            if 'OBRA' in tipo_objeto or 'ENGENHARIA' in tipo_objeto:
                amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 61), None)
            else:
                amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 62), None)
            tese_juridica = f"Enquadramento no Art. 75, inciso II da Lei nº 14.133/2021. O montante estimado de R$ {valor_estimado:,.2f} atende aos limites da contratação direta por valor, exigindo pesquisa de preços e verificação de não fracionamento."

    else:
        # Padrão: Licitação / Pregão Eletrônico
        modalidade_id = 6
        modalidade_nome = "Pregão Eletrônico (Licitação Pública)"
        amparo_escolhido = next((a for a in AMPAROS_PNCP if a['id'] == 200), None)
        tese_juridica = "Enquadramento como procedimento licitatório na modalidade Pregão Eletrônico (Art. 28, I da Lei nº 14.133/2021). O objeto caracteriza-se como bem ou serviço comum com padrões mercadológicos objetivos e ampla competitividade."

    if not amparo_escolhido:
        amparo_escolhido = AMPAROS_PNCP[0]

    # ── 2. PARECER DE RISCOS E JURISPRUDÊNCIA DO TCU ──
    alertas_tcu = []
    itens_checklist = []
    risco_nivel = "BAIXO"
    risco_cor = "green"

    if modalidade_id == 8:
        # Dispensa de Licitação
        if valor_estimado > (limite_dispensa_aplicavel * 0.85):
            alertas_tcu.append(f"⚠️ Atenção à margem orçamentária: O valor R$ {valor_estimado:,.2f} está muito próximo do teto legal (R$ {limite_dispensa_aplicavel:,.2f}). Pequenas variações de cotação podem desenquadrar a dispensa.")
            risco_nivel = "MEDIO"
            risco_cor = "yellow"
        
        alertas_tcu.append("🛡️ Risco de Fracionamento (Art. 75, § 1º da Lei 14.133/2021): A unidade demandante deve certificar que não realizou outras contratações de idêntica natureza durante o mesmo exercício financeiro cujo somatório ultrapasse o limite legal.")
        itens_checklist.append("Realizar pesquisa formal de preços com no mínimo 3 cotações idôneas ou parâmetros do Painel de Preços (Art. 23).")
        itens_checklist.append("Certidão da GCC confirmando que a despesa não ultrapassa o limite anual da mesma subfunção/natureza.")
        itens_checklist.append("Aviso de dispensa publicado no PNCP pelo prazo mínimo de 3 dias úteis para disputa eletrônica ou comprovação de preço manifestamente vantajoso.")

    elif modalidade_id == 9:
        # Inexigibilidade
        risco_nivel = "ALTO"
        risco_cor = "red"
        if is_exclusivo:
            alertas_tcu.append("⚖️ Súmula 255/TCU: A comprovação da exclusividade de fornecimento deve ser feita por atestado emitido pelo órgão de registro do comércio ou sindicato/federação da indústria, sendo vedada carta de exclusividade emitida pela própria empresa ou preferência de marca sem respaldo técnico.")
            itens_checklist.append("Juntada de Atestado Oficial de Exclusividade emitido por entidade patronal/sindicato válido.")
            itens_checklist.append("Justificativa circunstanciada de que nenhum outro produto similar no mercado atende às necessidades operacionais.")
            itens_checklist.append("Demonstração da razoabilidade do preço contratado mediante notas fiscais de vendas anteriores a outros órgãos públicos ou empresas privadas.")
        else:
            alertas_tcu.append("⚖️ Jurisprudência TCU (Acórdãos 2.616/2015 e 1.250/2018): Para serviços de notória especialização, exige-se demonstrar simultaneamente a singularidade do serviço e a notoriedade inconteste do profissional. Serviços rotineiros ou padronizados não admitem inexigibilidade.")
            itens_checklist.append("Comprovação curricular, prêmios, livros ou atuação prévia de vulto que caracterizem a notoriedade.")
            itens_checklist.append("Parecer demonstrando por que o serviço é singular e incompatível com o julgamento objetivo de propostas concorrentes.")

    elif modalidade_id == 10:
        # Credenciamento
        risco_nivel = "BAIXO"
        risco_cor = "blue"
        alertas_tcu.append("📋 Rito do Art. 79: O edital de credenciamento deve ficar permanentemente aberto e prever condições padronizadas de habilitação e remuneração idêntica para todos os prestadores.")
        itens_checklist.append("Publicação de edital permanente no PNCP.")
        itens_checklist.append("Tabela pública de preços e remuneração fixada previamente pela Administração.")

    else:
        # Pregão Eletrônico
        risco_nivel = "BAIXO"
        risco_cor = "green"
        alertas_tcu.append("✅ Modalidade preferencial e mais segura sob a ótica dos órgãos de controle. Garante ampla publicidade e competitividade.")
        itens_checklist.append("Elaboração de Estudo Técnico Preliminar (ETP) e Termo de Referência (TR).")
        itens_checklist.append("Pesquisa ampla de mercado em conformidade com a Instrução Normativa SEGES nº 65/2021.")

    # ── 3. MINUTA TÉCNICA E CAMPOS INFERIDOS PARA O CADASTRO ──
    # Lapidação do Objeto
    objeto_lapidado = objeto_raw if len(objeto_raw) > 20 else f"Contratação de {objeto_raw.lower() if objeto_raw else 'solução especializada'} para atendimento às demandas estratégicas da Telebras."
    if not objeto_lapidado.endswith('.'):
        objeto_lapidado += '.'

    # Justificativa formal
    justificativa_inferida = (
        f"A presente contratação é fundamental para assegurar a continuidade operacional e a excelência das atividades finalísticas da Telebras. "
        f"O enquadramento sob a modalidade {modalidade_nome} justifica-se tecnicamente e juridicamente com fulcro no {amparo_escolhido['nome']}, "
        f"tendo em vista que {tese_juridica.lower()}."
    )

    justificativa_nao_planejada = (
        "Contratação prioritária decorrente de necessidade superveniente de suporte operacional, "
        "não prevista no calendário regular de consolidação do plano, com impacto direto na estabilidade dos serviços."
    )

    # Datas de vigência
    hoje = datetime.now().date()
    # Prazo de instrução: 30 a 45 dias
    data_inicio_estimada = hoje + timedelta(days=45)
    # Prazo de vigência contratual: 12 meses (serviço ou continuado) ou 6 meses se for compra direta
    if is_continuo or 'SERVICO' in tipo_objeto:
        data_fim_estimada = data_inicio_estimada + timedelta(days=365)
    else:
        data_fim_estimada = data_inicio_estimada + timedelta(days=180)

    # Informações complementares
    info_complementares = (
        f"Regime Legal Aplicado: {regime_lei}\n"
        f"Modalidade Julgada: {modalidade_nome} (ID PNCP {modalidade_id})\n"
        f"Amparo Legal Selecionado: {amparo_escolhido['nome']}\n"
        f"Critério de Julgamento: {'Não se aplica' if modalidade_id in [8, 9] else 'Menor Preço Global'}\n"
        f"Modo de Disputa: {'Não se aplica' if modalidade_id in [8, 9] else 'Aberto/Fechado'}\n"
        f"Local de Prestação/Entrega: Sede Telebras - SIG Quadra 04, Bloco A, Brasília/DF - CEP 70610-440."
    )

    # Sugestão de Item de Contratação (CATMAT/CATSER)
    tipo_item_sigla = "S" if 'SERVICO' in tipo_objeto else "M"
    cat_sugerido = "SV-00124" if tipo_item_sigla == "S" else "MAT-00982"
    desc_item = objeto_lapidado[:500]
    
    # Quantidade de parcelas ou unidades
    qtd_item = 12.0 if is_continuo else 1.0
    val_unit = valor_estimado / qtd_item if qtd_item > 0 else valor_estimado

    itens_sugeridos = [{
        "numeroItem": 1,
        "tipo": tipo_item_sigla,
        "materialOuServico": "Serviço" if tipo_item_sigla == "S" else "Material",
        "codigo": cat_sugerido,
        "descricao": desc_item,
        "quantidade": qtd_item,
        "unidadeMedida": "MÊS" if is_continuo else "UN",
        "valorUnitarioEstimado": round(val_unit, 2),
        "valorTotal": round(valor_estimado, 2),
        "orcamentoSigiloso": False,
        "tipoBeneficioId": "1"
    }]

    return {
        "veredito": {
            "modalidade_id": modalidade_id,
            "modalidade_nome": modalidade_nome,
            "amparo_legal_id": amparo_escolhido["id"],
            "amparo_legal_nome": amparo_escolhido["nome"],
            "amparo_legal_artigo": amparo_escolhido["artigo"],
            "amparo_legal_inciso": amparo_escolhido["inciso"],
            "amparo_legal_texto": amparo_escolhido["descricao"],
            "tese_juridica": tese_juridica,
            "regime_lei": regime_lei
        },
        "auditoria_riscos_tcu": {
            "nivel_risco": risco_nivel,
            "cor_risco": risco_cor,
            "alertas": alertas_tcu,
            "checklist_obrigatorio": itens_checklist,
            "blindagem_jurisprudencial": amparo_escolhido.get("requisitos_tcu", "")
        },
        "dados_formulario_compra": {
            "titulo": f"Contratação - {modalidade_nome.split(' (')[0]} - {datetime.now().year}",
            "numero_processo": f"53000.00{datetime.now().strftime('%m%d')}/{datetime.now().year}-10",
            "objeto": objeto_lapidado,
            "justificativa": justificativa_inferida,
            "justificativa_nao_planejada": justificativa_nao_planejada,
            "informacoes_complementares": info_complementares,
            "modalidade_id": modalidade_id,
            "amparo_legal_id": amparo_escolhido["id"],
            "modo_disputa": "Não se aplica" if modalidade_id in [8, 9] else "Dispensa com Disputa",
            "data_inicio": data_inicio_estimada.strftime('%Y-%m-%d'),
            "data_fim": data_fim_estimada.strftime('%Y-%m-%d'),
            "valor_total_estimado": valor_estimado,
            "itens": itens_sugeridos
        }
    }
