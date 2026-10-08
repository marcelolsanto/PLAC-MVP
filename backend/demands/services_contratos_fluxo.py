import os
import re
from datetime import datetime, date, timedelta

# Definição canônica das 7 macro-áreas da Telebras no Fluxo Lógico
AREAS_TELEBRAS = [
    {
        "id": "requisitante",
        "nome": "1. Área Requisitante / Técnica",
        "sigla": "REQUISITANTE",
        "setores_exemplos": ["GTI (4200)", "GLOG (3600)", "GROP (3200)", "GGE (2100)", "GPTC (3500)"],
        "atividades": "Formalização da Demanda (DOD/DFD), ETP, Termo de Referência, Indicação de Fiscal",
        "responsavel_padrao": "Gestor / Fiscal da Área Demandante",
        "sla_dias": 15,
        "cor": "blue"
    },
    {
        "id": "gcc",
        "nome": "2. GCC - Compras & Contratações",
        "sigla": "GCC",
        "setores_exemplos": ["GCC", "GCE"],
        "atividades": "Termo de Enquadramento, Pesquisa de Preços (IN 65), Minutas de Edital/Contrato/Aditivo",
        "responsavel_padrao": "Layllah / Marcus / Franciele / Roberta",
        "sla_dias": 20,
        "cor": "purple"
    },
    {
        "id": "gefin",
        "nome": "3. GEFIN / GEOF - Orçamento & Finanças",
        "sigla": "GEFIN",
        "setores_exemplos": ["GEFIN", "GEOF", "DIRAF"],
        "atividades": "DIF (Declaração Orçamentária e Financeira), Dotação SAP, Empenho Prévio",
        "responsavel_padrao": "Equipe de Gestão Orçamentária",
        "sla_dias": 5,
        "cor": "amber"
    },
    {
        "id": "conjur",
        "nome": "4. CONJUR - Consultoria Jurídica",
        "sigla": "CONJUR",
        "setores_exemplos": ["CONJUR", "Procuradoria"],
        "atividades": "Análise de Legalidade, Minuta de Contrato/Aditivo, Parecer Jurídico Art. 53/Art. 73",
        "responsavel_padrao": "Dr. Fernando Rocha - Procurador Consultivo",
        "sla_dias": 15,
        "cor": "rose"
    },
    {
        "id": "diretoria",
        "nome": "5. Diretoria Executiva / Ordenador",
        "sigla": "DIRETORIA",
        "setores_exemplos": ["PRESI", "DAFRI", "Alencastro", "REDIR"],
        "atividades": "Autorização de Abertura, Deliberação da Diretoria, Homologação e Assinatura",
        "responsavel_padrao": "Alencastro / Tatiana Miranda / Diretoria Executiva",
        "sla_dias": 5,
        "cor": "indigo"
    },
    {
        "id": "pncp",
        "nome": "6. Publicação PNCP / DOU",
        "sigla": "PNCP/DOU",
        "setores_exemplos": ["GCC - Publicações", "Imprensa Nacional"],
        "atividades": "Publicação obrigatória de Extrato de Contrato ou Termo Aditivo no PNCP e DOU",
        "responsavel_padrao": "Pedro / Rosilda",
        "sla_dias": 3,
        "cor": "cyan"
    },
    {
        "id": "gecad",
        "nome": "7. GECAD / Gestão Contratual & Fiscalização",
        "sigla": "GECAD",
        "setores_exemplos": ["GECAD", "GCONT", "Fiscais Designados"],
        "atividades": "Cadastro SAP, Emissão da DEG (Designação do Fiscal), SLA de Entrega, Medição e Ateste",
        "responsavel_padrao": "Gerência de Cadastro de Contratos / Fiscal Titular",
        "sla_dias": 365,
        "cor": "emerald"
    }
]

def _extrair_contratos_do_banco():
    from .models import Contract
    qs = Contract.objects.select_related('processo_siga', 'processo_siga__demand').all()
    dados = []
    for idx, c in enumerate(qs, start=1):
        demand = c.processo_siga.demand if c.processo_siga else None
        
        dir_nome = "Desconhecida"
        area_req = "Desconhecida"
        if demand:
            dir_nome = demand.directorate or dir_nome
            area_req = demand.management_unit or area_req
            
        dados.append({
            "id": c.id or idx,
            "numero_contrato": c.numero_contrato,
            "numero_processo_siga": c.processo_siga.numero_processo if c.processo_siga else "N/A",
            "fornecedor": c.fornecedor or "Não Informado",
            "cnpj_cpf": c.cnpj_cpf or "Não Informado",
            "objeto": c.objeto or "Sem objeto",
            "modalidade": c.modalidade or "Não Informado",
            "fundamentacao_legal": "Lei 14.133/2021",
            "valor_global": float(c.valor_global or 0.0),
            "data_inicio_vigencia": str(c.data_inicio_vigencia) if c.data_inicio_vigencia else "",
            "data_fim_vigencia": str(c.data_fim_vigencia) if c.data_fim_vigencia else "",
            "diretoria": dir_nome,
            "area_requisitante": area_req,
            "fiscal_titular": demand.responsible_name if demand else "Designado",
            "area_atual_tramitacao": c.processo_siga.setor_atual.lower() if c.processo_siga and c.processo_siga.setor_atual else "gecad",
            "dias_na_area_atual": c.dias_na_area_atual,
            "ultimo_despacho_siga": c.ultimo_despacho_siga or "Sem despacho",
            "pncp_id": c.pncp_id or "",
            "situacao_pncp": c.situacao_pncp or "Ativo",
            "link_pncp": c.link_pncp or ""
        })
    return dados

def get_contratos_pncp():
    return _extrair_contratos_do_banco()

def obter_resumo_fluxo_areas_telebras():
    base_contratos = _extrair_contratos_do_banco()
    resumo = {area["id"]: {"info": area, "contratos_aqui": 0, "valor_acumulado": 0.0} for area in AREAS_TELEBRAS}
    total_ativos = 0
    
    for c in base_contratos:
        area_id = c.get("area_atual_tramitacao")
        if area_id in resumo:
            resumo[area_id]["contratos_aqui"] += 1
            resumo[area_id]["valor_acumulado"] += c.get("valor_global", 0.0)
            total_ativos += 1
            
    return {
        "timestamp": datetime.now().isoformat(),
        "total_contratos_fluxo": total_ativos,
        "areas": [resumo[a["id"]] for a in AREAS_TELEBRAS]
    }

def obter_tempo_medio_areas():
    base_contratos = _extrair_contratos_do_banco()
    metricas = []
    
    for area in AREAS_TELEBRAS:
        area_id = area["id"]
        contratos_area = [c for c in base_contratos if c.get("area_atual_tramitacao") == area_id]
        
        qtd = len(contratos_area)
        tempo_medio = 0
        gargalos = 0
        if qtd > 0:
            tempos = [c.get("dias_na_area_atual", 0) for c in contratos_area]
            tempo_medio = sum(tempos) / qtd
            gargalos = len([t for t in tempos if t > area["sla_dias"]])
            
        metricas.append({
            "area_id": area_id,
            "sigla": area["sigla"],
            "sla_dias": area["sla_dias"],
            "tempo_medio_atual": round(tempo_medio, 1),
            "quantidade_processos": qtd,
            "alertas_gargalo": gargalos
        })
        
    return {"metricas_tempo": metricas}

def obter_processo_paradigma():
    base_contratos = _extrair_contratos_do_banco()
    if not base_contratos:
        return {"paradigma": None}
    
    rapido = min(base_contratos, key=lambda c: c.get("dias_na_area_atual", 999))
    return {
        "paradigma": {
            "contrato": rapido["numero_contrato"],
            "fornecedor": rapido["fornecedor"],
            "dias_tramitacao_total": 45,
            "motivo_agilidade": "DOD bem instruído, TR objetivo e Parecer Referencial.",
            "tempo_economizado": "30 dias"
        }
    }

def obter_kanban_areas():
    base_contratos = _extrair_contratos_do_banco()
    kanban = []
    for area in AREAS_TELEBRAS:
        area_id = area["id"]
        kanban.append({
            "coluna_id": area_id,
            "titulo": area["nome"],
            "cor": area["cor"],
            "cards": [c for c in base_contratos if c.get("area_atual_tramitacao") == area_id]
        })
    return {"kanban": kanban}
