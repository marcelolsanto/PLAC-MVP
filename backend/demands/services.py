ALLOWED_SCORES = {1, 3, 5}

def calculate_priority(f1: int, f2: int, f3: int, f4: int) -> tuple[int, str]:
    """
    Calcula a pontuação e o grau de prioridade com base na fórmula do UC01:
    Score = (F1 × 30) + (F2 × 30) + (F3 × 25) + (F4 × 15)
    Notas válidas: 1, 3 ou 5
    """
    for factor_name, val in [("F1", f1), ("F2", f2), ("F3", f3), ("F4", f4)]:
        if val not in ALLOWED_SCORES:
            raise ValueError(f"Fator {factor_name} inválido ({val}). Notas permitidas são apenas 1, 3 ou 5.")

    score = (f1 * 30) + (f2 * 30) + (f3 * 25) + (f4 * 15)

    if score >= 380:
        level = 'ALTO'
    elif score >= 240:
        level = 'MEDIO'
    else:
        level = 'BAIXO'

    return score, level

SLA_MAP = {
    'PREGAO': 157,
    'DISPENSA': 45,
    'INEXIGIBILIDADE': 60,
    'CONCORRENCIA': 180,
}

from datetime import date, timedelta

def calculate_sla_deadline(intended_date: date, procurement_type: str) -> tuple[date, int, bool]:
    """
    Subtrai o prazo de SLA da data pretendida de assinatura.
    Retorna (data_limite, sla_dias, necessita_antecipacao_ano_anterior)
    """
    sla_days = SLA_MAP.get(procurement_type, 157)
    deadline = intended_date - timedelta(days=sla_days)
    needs_anticipation = deadline.year < intended_date.year
    return deadline, sla_days, needs_anticipation
