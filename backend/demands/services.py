"""
Serviço de Prazos e Prioridades das Demandas do PLAC
Delega a lógica de cálculo para o módulo regimental services_minuta_plac.py,
mantendo compatibilidade com as rotas e views legadas.
"""

from datetime import date
from .services_minuta_plac import (
    ALLOWED_NOTES as ALLOWED_SCORES,
    calcular_prioridade_minuta,
    calcular_calendario_anexo_iii,
    PRAZOS_ANEXO_III,
    TIPO_CONTRATACAO_ALIASES,
)

# Mapa para retrocompatibilidade
SLA_MAP = {
    'PREGAO': 140,
    'DISPENSA': 92,
    'INEXIGIBILIDADE': 88,
    'CONCORRENCIA': 140,
}


def calculate_priority(
    f1: int,
    f2: int,
    f3: int,
    f4: int,
    substitui_contrato_expirando: bool = False,
    obrigacao_legal_prazo_fatal: bool = False,
) -> tuple[int, str]:
    """
    Calcula a pontuação e o grau de prioridade com base no Anexo II da Minuta do PLAC:
    Score = (F1 × 30) + (F2 × 30) + (F3 × 25) + (F4 × 15)
    Notas válidas: 1, 3 ou 5
    """
    res = calcular_prioridade_minuta(
        f1=f1,
        f2=f2,
        f3=f3,
        f4=f4,
        substitui_contrato_expirando=substitui_contrato_expirando,
        obrigacao_legal_prazo_fatal=obrigacao_legal_prazo_fatal,
    )
    return res["pontuacao"], res["grau_prioridade"]


def calculate_sla_deadline(intended_date: date, procurement_type: str) -> tuple[date, int, bool]:
    """
    Subtrai o prazo regimental em dias úteis da data pretendida de assinatura (Anexo III).
    Retorna (data_limite, sla_dias_uteis, necessita_antecipacao_ano_anterior)
    """
    res = calcular_calendario_anexo_iii(intended_date, procurement_type)
    data_limite = date.fromisoformat(res["data_limite_envio_gcc"])
    return data_limite, res["dias_uteis_ate_assinatura"], res["alerta_antecipacao"]
