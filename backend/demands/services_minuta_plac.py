"""
Serviço Regimental da Diretriz do PLAC da Telebras (Minuta v2 - Regulamentação do Art. 16 do RELIC)
Implementa as regras, tabelas e fórmulas dos Anexos da Minuta:
- Anexo I: Modelo de Registro de Necessidade (Blocos 1 a 6)
- Anexo II: Metodologia de Priorização das Contratações (F1..F4, fórmula ponderada e travas obrigatórias)
- Anexo III: Prazos Estimados em Dias Úteis e Cálculo da Data-Limite de Envio com Alerta de Antecipação
- Anexo IV: Indicadores Oficiais de Desempenho do PLAC (TEP, IAC, ICNP, IAP, TMP)
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
import os
import json

ALLOWED_NOTES = {1, 3, 5}

# ─────────────────────────────────────────────────────────────────────────────
# ANEXO III - PRAZOS DE REFERÊNCIA POR TIPO DE CONTRATAÇÃO (DIAS ÚTEIS)
# ─────────────────────────────────────────────────────────────────────────────
PRAZOS_ANEXO_III: Dict[str, Dict[str, Any]] = {
    "PREGAO_ELETRONICO": {
        "codigo": "PREGAO_ELETRONICO",
        "nome": "Pregão Eletrônico",
        "etapas": 36,
        "dias_uteis_ate_assinatura": 140,
        "dias_uteis_pos_assinatura": 17,
        "dias_uteis_total": 157,
        "meses_aprox": 7.5,
    },
    "DISPENSA_TRADICIONAL": {
        "codigo": "DISPENSA_TRADICIONAL",
        "nome": "Dispensa tradicional",
        "etapas": 32,
        "dias_uteis_ate_assinatura": 92,
        "dias_uteis_pos_assinatura": 17,
        "dias_uteis_total": 109,
        "meses_aprox": 5.2,
    },
    "DISPENSA_BAIXO_VALOR": {
        "codigo": "DISPENSA_BAIXO_VALOR",
        "nome": "Dispensa tradicional de baixo valor",
        "etapas": 32,
        "dias_uteis_ate_assinatura": 90,
        "dias_uteis_pos_assinatura": 17,
        "dias_uteis_total": 107,
        "meses_aprox": 5.1,
    },
    "DISPENSA_BAIXO_VALOR_ELETRONICA": {
        "codigo": "DISPENSA_BAIXO_VALOR_ELETRONICA",
        "nome": "Dispensa de baixo valor - eletrônica",
        "etapas": 35,
        "dias_uteis_ate_assinatura": 81,
        "dias_uteis_pos_assinatura": 21,
        "dias_uteis_total": 102,
        "meses_aprox": 4.9,
    },
    "INEXIGIBILIDADE": {
        "codigo": "INEXIGIBILIDADE",
        "nome": "Inexigibilidade",
        "etapas": 31,
        "dias_uteis_ate_assinatura": 88,
        "dias_uteis_pos_assinatura": 17,
        "dias_uteis_total": 105,
        "meses_aprox": 5.0,
    },
    "INEXIGIBILIDADE_CURSOS": {
        "codigo": "INEXIGIBILIDADE_CURSOS",
        "nome": "Inexigibilidade - contratação de cursos",
        "etapas": 15,
        "dias_uteis_ate_assinatura": 20,
        "dias_uteis_pos_assinatura": 2,
        "dias_uteis_total": 22,
        "meses_aprox": 1.0,
    },
    "DISPENSA_LOCACAO": {
        "codigo": "DISPENSA_LOCACAO",
        "nome": "Dispensa - contratos de locação",
        "etapas": 19,
        "dias_uteis_ate_assinatura": 40,
        "dias_uteis_pos_assinatura": 12,
        "dias_uteis_total": 52,
        "meses_aprox": 2.5,
    },
    "DISPENSA_ENERGIA": {
        "codigo": "DISPENSA_ENERGIA",
        "nome": "Dispensa - energia elétrica",
        "etapas": 20,
        "dias_uteis_ate_assinatura": 37,
        "dias_uteis_pos_assinatura": 11,
        "dias_uteis_total": 48,
        "meses_aprox": 2.3,
    },
    "INEXIGIBILIDADE_COMPARTILHAMENTO": {
        "codigo": "INEXIGIBILIDADE_COMPARTILHAMENTO",
        "nome": "Inexigibilidade - compartilhamento de infraestrutura",
        "etapas": 23,
        "dias_uteis_ate_assinatura": 59,
        "dias_uteis_pos_assinatura": 13,
        "dias_uteis_total": 72,
        "meses_aprox": 3.4,
    },
    "AFASTAMENTO_ART_117": {
        "codigo": "AFASTAMENTO_ART_117",
        "nome": "Afastamento das regras de licitação (art. 117 do RELIC)",
        "etapas": 30,
        "dias_uteis_ate_assinatura": 87,
        "dias_uteis_pos_assinatura": 14,
        "dias_uteis_total": 101,
        "meses_aprox": 4.8,
    },
}

# Alias comum para compatibilidade com nomes antigos
TIPO_CONTRATACAO_ALIASES = {
    "PREGAO": "PREGAO_ELETRONICO",
    "PREGÃO ELETRÔNICO": "PREGAO_ELETRONICO",
    "DISPENSA": "DISPENSA_TRADICIONAL",
    "INEXIGIBILIDADE": "INEXIGIBILIDADE",
    "CURSOS": "INEXIGIBILIDADE_CURSOS",
    "LOCACAO": "DISPENSA_LOCACAO",
    "ENERGIA": "DISPENSA_ENERGIA",
    "COMPARTILHAMENTO": "INEXIGIBILIDADE_COMPARTILHAMENTO",
    "AFASTAMENTO": "AFASTAMENTO_ART_117",
}


def subtrair_dias_uteis(data_referencia: date, dias_uteis: int) -> date:
    """
    Subtrai dias úteis de uma data considerando fins de semana (sábado e domingo).
    Pode ser expandido com feriados nacionais.
    """
    data_atual = data_referencia
    dias_restantes = dias_uteis
    while dias_restantes > 0:
        data_atual -= timedelta(days=1)
        if data_atual.weekday() < 5:
            dias_restantes -= 1
    return data_atual


def somar_dias_uteis(data_referencia: date, dias_uteis: int) -> date:
    """Soma dias úteis a uma data considerando fins de semana."""
    data_atual = data_referencia
    dias_restantes = dias_uteis
    while dias_restantes > 0:
        data_atual += timedelta(days=1)
        if data_atual.weekday() < 5:
            dias_restantes -= 1
    return data_atual


# ─────────────────────────────────────────────────────────────────────────────
# ANEXO II - METODOLOGIA DE PRIORIZAÇÃO DAS CONTRATAÇÕES
# ─────────────────────────────────────────────────────────────────────────────
def calcular_prioridade_minuta(
    f1: int,
    f2: int,
    f3: int,
    f4: int,
    substitui_contrato_expirando: bool = False,
    sem_possibilidade_prorrogacao: bool = False,
    obrigacao_legal_prazo_fatal: bool = False,
    marco_terceiros_definido: bool = False,
) -> Dict[str, Any]:
    """
    Aplica a metodologia do Anexo II da Minuta da Diretriz do PLAC:
    Fórmula: P = (F1 × 30) + (F2 × 30) + (F3 × 25) + (F4 × 15)
    Notas válidas: 1, 3 ou 5.
    
    Regras de enquadramento obrigatório (Item 6):
    - Se indispensável ao cumprimento de obrigação legal/determinação com prazo fatal -> ALTO
    - Se substituição de contrato vigente que expira no exercício sem prorrogação -> ALTO
    - Se vinculado a marco contratual perante terceiros -> ALTO
    
    Vedação (Item 7):
    - É vedada a classificação como BAIXO de contratação destinada a substituir contrato que expire no exercício.
    """
    for nome, val in [("F1", f1), ("F2", f2), ("F3", f3), ("F4", f4)]:
        if val not in ALLOWED_NOTES:
            raise ValueError(f"Fator {nome} inválido ({val}). As notas permitidas são apenas 1, 3 ou 5.")

    pontuacao = (f1 * 30) + (f2 * 30) + (f3 * 25) + (f4 * 15)

    # Classificação base por pontuação
    if pontuacao >= 380:
        grau_calculado = "ALTO"
    elif pontuacao >= 240:
        grau_calculado = "MEDIO"
    else:
        grau_calculado = "BAIXO"

    # Aplicação das regras de enquadramento obrigatório (Item 6)
    enquadramento_obrigatorio = False
    motivo_enquadramento = None

    if obrigacao_legal_prazo_fatal or (f3 == 5):
        grau = "ALTO"
        enquadramento_obrigatorio = True
        motivo_enquadramento = "Obrigação legal, regulatória ou determinação de órgão de controle com prazo fatal no exercício (Item 6.a)"
    elif sem_possibilidade_prorrogacao or (f2 == 5):
        grau = "ALTO"
        enquadramento_obrigatorio = True
        motivo_enquadramento = "Substituição de contrato vigente que expira no exercício sem possibilidade de prorrogação (Item 6.b)"
    elif marco_terceiros_definido:
        grau = "ALTO"
        enquadramento_obrigatorio = True
        motivo_enquadramento = "Vinculado a marco contratual perante terceiros com data definida no exercício (Item 6.c)"
    else:
        grau = grau_calculado

    # Aplicação da vedação do Item 7 (vedada classificação como Baixo para substituição de contrato)
    if substitui_contrato_expirando and grau == "BAIXO":
        grau = "MEDIO"
        motivo_enquadramento = "Vedada prioridade baixa para contratação que substitui contrato a expirar (Item 7)"

    # Efeito no Calendário de Contratação (Item 5 e 6)
    if grau == "ALTO":
        quadrimestre_limite = "1º Quadrimestre (até Abril)"
        quadrimestre_id = "1Q"
    elif grau == "MEDIO":
        quadrimestre_limite = "2º Quadrimestre (até Agosto)"
        quadrimestre_id = "2Q"
    else:
        quadrimestre_limite = "3º Quadrimestre (até Dezembro)"
        quadrimestre_id = "3Q"

    return {
        "pontuacao": pontuacao,
        "grau_prioridade": grau,
        "grau_calculado_original": grau_calculado,
        "enquadramento_obrigatorio": enquadramento_obrigatorio,
        "motivo_enquadramento": motivo_enquadramento,
        "quadrimestre_limite": quadrimestre_limite,
        "quadrimestre_id": quadrimestre_id,
        "fatores": {
            "f1_criticidade": f1,
            "f2_descontinuidade": f2,
            "f3_obrigacao_legal": f3,
            "f4_materialidade": f4,
        },
    }


# ─────────────────────────────────────────────────────────────────────────────
# ANEXO III - CÁLCULO DE DATA-LIMITE E ALERTA DE ANTECIPAÇÃO
# ─────────────────────────────────────────────────────────────────────────────
def calcular_calendario_anexo_iii(
    data_pretendida_assinatura: date,
    tipo_contratacao: str,
    dias_preparatoria_demandante: int = 45,
) -> Dict[str, Any]:
    """
    Aplica o algoritmo do Anexo III da Minuta:
    Data-limite = Data pretendida de assinatura − Prazo até a assinatura (dias úteis)
    Início Preparatória = Data-limite − Prazo fase preparatória demandante
    
    Verifica se a data-limite recai em exercício anterior -> Alerta de Antecipação.
    """
    chave_tipo = TIPO_CONTRATACAO_ALIASES.get(tipo_contratacao.upper(), tipo_contratacao.upper())
    config_tipo = PRAZOS_ANEXO_III.get(chave_tipo, PRAZOS_ANEXO_III["PREGAO_ELETRONICO"])

    dias_uteis_ate_assinatura = config_tipo["dias_uteis_ate_assinatura"]
    dias_uteis_pos = config_tipo["dias_uteis_pos_assinatura"]
    dias_uteis_total = config_tipo["dias_uteis_total"]

    # Cálculo da data-limite de envio para a GCC
    data_limite_envio_gcc = subtrair_dias_uteis(data_pretendida_assinatura, dias_uteis_ate_assinatura)

    # Cálculo da data recomendada para início da fase preparatória na área requisitante
    data_inicio_preparatoria = subtrair_dias_uteis(data_limite_envio_gcc, dias_preparatoria_demandante)

    # Alerta de antecipação (Item 6): recai em ano anterior
    alerta_antecipacao = data_limite_envio_gcc.year < data_pretendida_assinatura.year

    return {
        "tipo_contratacao": config_tipo["nome"],
        "tipo_contratacao_codigo": config_tipo["codigo"],
        "dias_uteis_ate_assinatura": dias_uteis_ate_assinatura,
        "dias_uteis_pos_assinatura": dias_uteis_pos,
        "dias_uteis_total": dias_uteis_total,
        "meses_aproximados": config_tipo["meses_aprox"],
        "data_pretendida_assinatura": data_pretendida_assinatura.isoformat(),
        "data_limite_envio_gcc": data_limite_envio_gcc.isoformat(),
        "data_inicio_preparatoria_recomendada": data_inicio_preparatoria.isoformat(),
        "alerta_antecipacao": alerta_antecipacao,
        "ano_exercicio_execucao": data_pretendida_assinatura.year,
        "ano_envio_gcc": data_limite_envio_gcc.year,
    }


# ─────────────────────────────────────────────────────────────────────────────
# ANEXO IV - INDICADORES DE DESEMPENHO DO PLAC (ART. 47)
# ─────────────────────────────────────────────────────────────────────────────
def calcular_indicadores_anexo_iv(
    contratacoes_planejadas: int,
    contratacoes_concluidas: int,
    processos_encaminhados_no_prazo: int,
    processos_encaminhados_total: int,
    itens_incluidos_no_curso: int,
    total_itens_plac_vigente: int,
    alteracoes_aprovadas: int,
    soma_dias_uteis_reais: int,
    concluidas_com_tempo: int,
    processos_devolvidos_incompletude: int = 0,
    soma_dias_saneamento: int = 0,
) -> Dict[str, Any]:
    """
    Calcula os 5 indicadores oficiais do Art. 47 e Anexo IV:
    I - TEP: Taxa de Execução do PLAC (Meta: >= 85% Verde, 70-84% Amarelo, < 70% Vermelho)
    II - IAC: Índice de Aderência ao Calendário (Meta: >= 90% Verde, 75-89% Amarelo, < 75% Vermelho)
    III - ICNP: Índice de Contratações Não Planejadas (Meta: <= 10% Verde, 11-20% Amarelo, > 20% Vermelho)
    IV - IAP: Índice de Alterações do Plano (Meta: <= 25% Verde, 26-40% Amarelo, > 40% Vermelho)
    V - TMP: Tempo Médio de Processamento (Comparação com Anexo III)
    """
    # 1. TEP
    tep = round((contratacoes_concluidas / contratacoes_planejadas * 100), 1) if contratacoes_planejadas > 0 else 0.0
    if tep >= 85.0:
        tep_status, tep_cor = "Adequado", "emerald"
    elif tep >= 70.0:
        tep_status, tep_cor = "Atenção", "amber"
    else:
        tep_status, tep_cor = "Crítico", "rose"

    # 2. IAC
    iac = round((processos_encaminhados_no_prazo / processos_encaminhados_total * 100), 1) if processos_encaminhados_total > 0 else 100.0
    if iac >= 90.0:
        iac_status, iac_cor = "Adequado", "emerald"
    elif iac >= 75.0:
        iac_status, iac_cor = "Atenção", "amber"
    else:
        iac_status, iac_cor = "Crítico", "rose"

    # 3. ICNP
    icnp = round((itens_incluidos_no_curso / total_itens_plac_vigente * 100), 1) if total_itens_plac_vigente > 0 else 0.0
    if icnp <= 10.0:
        icnp_status, icnp_cor = "Adequado", "emerald"
    elif icnp <= 20.0:
        icnp_status, icnp_cor = "Atenção", "amber"
    else:
        icnp_status, icnp_cor = "Crítico", "rose"

    # 4. IAP
    iap = round((alteracoes_aprovadas / total_itens_plac_vigente * 100), 1) if total_itens_plac_vigente > 0 else 0.0
    if iap <= 25.0:
        iap_status, iap_cor = "Adequado", "emerald"
    elif iap <= 40.0:
        iap_status, iap_cor = "Atenção", "amber"
    else:
        iap_status, iap_cor = "Crítico", "rose"

    # 5. TMP
    tmp_dias_uteis = round(soma_dias_uteis_reais / concluidas_com_tempo, 1) if concluidas_com_tempo > 0 else 0.0
    
    # Indicadores complementares
    taxa_devolucao = round((processos_devolvidos_incompletude / processos_encaminhados_total * 100), 1) if processos_encaminhados_total > 0 else 0.0
    tempo_medio_saneamento = round(soma_dias_saneamento / processos_devolvidos_incompletude, 1) if processos_devolvidos_incompletude > 0 else 0.0

    return {
        "tep": {
            "sigla": "TEP",
            "valor": tep,
            "status": tep_status,
            "cor": tep_cor,
            "meta": "≥ 85%",
            "descricao": "Taxa de Execução do PLAC (Efetividade do Planejamento)",
            "concluidas": contratacoes_concluidas,
            "planejadas": contratacoes_planejadas,
        },
        "iac": {
            "sigla": "IAC",
            "valor": iac,
            "status": iac_status,
            "cor": iac_cor,
            "meta": "≥ 90%",
            "descricao": "Índice de Aderência ao Calendário (Disciplina das Áreas Demandantes)",
            "encaminhados_no_prazo": processos_encaminhados_no_prazo,
            "total_encaminhados": processos_encaminhados_total,
        },
        "icnp": {
            "sigla": "ICNP",
            "valor": icnp,
            "status": icnp_status,
            "cor": icnp_cor,
            "meta": "≤ 10%",
            "descricao": "Índice de Contratações Não Planejadas (Qualidade da Previsão Inicial)",
            "itens_incluidos": itens_incluidos_no_curso,
            "total_vigente": total_itens_plac_vigente,
        },
        "iap": {
            "sigla": "IAP",
            "valor": iap,
            "status": iap_status,
            "cor": iap_cor,
            "meta": "≤ 25%",
            "descricao": "Índice de Alterações do Plano (Estabilidade das Demandas)",
            "alteracoes": alteracoes_aprovadas,
            "total_vigente": total_itens_plac_vigente,
        },
        "tmp": {
            "sigla": "TMP",
            "valor_dias_uteis": tmp_dias_uteis,
            "meses_aprox": round(tmp_dias_uteis / 21, 1),
            "concluidas_amostra": concluidas_com_tempo,
            "descricao": "Tempo Médio de Processamento (Desempenho Real da GCC)",
        },
        "complementares": {
            "taxa_devolucao_instrucao_incompleta": taxa_devolucao,
            "tempo_medio_saneamento_dias": tempo_medio_saneamento,
            "devolucoes_total": processos_devolvidos_incompletude,
        },
    }
