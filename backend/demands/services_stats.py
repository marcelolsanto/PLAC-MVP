"""
Módulo de Inferência Estatística Amostral e Previsão Probabilística (PERT / Intervalos de Confiança)
Calibrado dinamicamente com os dados reais do banco de dados (SigaProcess e Contract).
"""

import math
import statistics
from datetime import datetime, date, timedelta

def extrair_dias_uteis_do_banco(modalidade_nome):
    from .models import Contract
    contratos = Contract.objects.filter(modalidade__icontains=modalidade_nome).select_related('processo_siga')
    
    amostras = []
    for c in contratos:
        if c.processo_siga and c.processo_siga.data_autuacao and c.data_inicio_vigencia:
            # Cálculo simplificado de dias entre autuação e contrato
            delta = (c.data_inicio_vigencia - c.processo_siga.data_autuacao).days
            if delta > 0:
                # Aproximação de dias úteis (tira fins de semana)
                semanas = delta // 7
                dias_uteis = delta - (semanas * 2)
                amostras.append(dias_uteis)
                
    if not amostras:
        return [25] # fallback mínimo se vazio
    return amostras


def calcular_metricas_amostrais(dados):
    if not dados:
        return {}
    
    n = len(dados)
    media = statistics.mean(dados)
    desvio = statistics.stdev(dados) if n > 1 else 0.0
    mediana = statistics.median(dados)
    minimo = min(dados)
    maximo = max(dados)
    
    erro_padrao = desvio / math.sqrt(n) if n > 0 else 0.0
    ic_95_inf = max(0.0, media - 1.96 * erro_padrao)
    ic_95_sup = media + 1.96 * erro_padrao
    ic_80_inf = max(0.0, media - 1.282 * erro_padrao)
    ic_80_sup = media + 1.282 * erro_padrao
    
    return {
        "n_amostra": n,
        "media": round(media, 1),
        "mediana": round(mediana, 1),
        "desvio_padrao": round(desvio, 2),
        "erro_padrao": round(erro_padrao, 2),
        "minimo": minimo,
        "maximo": maximo,
        "ic_95": f"[{round(ic_95_inf, 1)}, {round(ic_95_sup, 1)}]",
        "ic_80": f"[{round(ic_80_inf, 1)}, {round(ic_80_sup, 1)}]"
    }

def obter_inferencia_fluxos():
    pregoes = extrair_dias_uteis_do_banco("Pregão")
    dispensas = extrair_dias_uteis_do_banco("Dispensa")
    
    return {
        "timestamp_analise": datetime.now().isoformat(),
        "pregao_eletronico": calcular_metricas_amostrais(pregoes),
        "dispensa_licitacao": calcular_metricas_amostrais(dispensas)
    }

def estimativa_pert(otimista, provavel, pessimista):
    te = (otimista + 4 * provavel + pessimista) / 6
    dp = (pessimista - otimista) / 6
    var = dp ** 2
    return round(te, 1), round(dp, 2)

def previsao_processo(modalidade, dias_passados=0, nivel_confianca=80):
    dados = extrair_dias_uteis_do_banco("Pregão") if "preg" in modalidade.lower() else extrair_dias_uteis_do_banco("Dispensa")
    m = calcular_metricas_amostrais(dados)
    
    te, dp = estimativa_pert(m["minimo"], m["mediana"], m["maximo"])
    dias_restantes = max(0, te - dias_passados)
    
    z = 1.282 if nivel_confianca == 80 else 1.645 if nivel_confianca == 90 else 1.96
    teto_restante = max(0, dias_restantes + (z * dp))
    
    return {
        "modalidade_avaliada": modalidade,
        "media_pert_te": te,
        "desvio_pert_dp": dp,
        "dias_passados": dias_passados,
        "dias_uteis_restantes_esperados": round(dias_restantes, 1),
        "teto_conservador": round(teto_restante, 1)
    }
