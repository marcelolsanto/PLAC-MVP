"""
Módulo de Gestão de Capacidade da GCC e Agendamento Reverso (Robô de Planejamento)
Implementa as regras de backward scheduling conforme os SLAs das 10 modalidades da GCC,
balizamento de saturação operacional e recomendação autônoma de janelas cabíveis no Calendário de Contratações.
"""

import math
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple, Any

from .services_stats import MODALIDADES_GCC_CONFIG, calcular_estatisticas_modalidade_99

# Feriados Nacionais Brasileiros e Pontos Facultativos Típicos (2024 a 2028)
# Base de referência para cálculo fidedigno de dias úteis da Administração Pública Federal
FERIADOS_FIXOS = [
    (1, 1),    # Confraternização Universal
    (4, 21),   # Tiradentes
    (5, 1),    # Dia do Trabalho
    (9, 7),    # Independência do Brasil
    (10, 12),  # Nossa Senhora Aparecida
    (11, 2),   # Finados
    (11, 15),  # Proclamação da República
    (11, 20),  # Dia Nacional de Zumbi e da Consciência Negra
    (12, 25),  # Natal
]

FERIADOS_MOVEIS_POR_ANO = {
    2024: [
        date(2024, 2, 12), date(2024, 2, 13), # Carnaval
        date(2024, 3, 29),                    # Sexta-feira Santa
        date(2024, 5, 30),                    # Corpus Christi
    ],
    2025: [
        date(2025, 3, 3), date(2025, 3, 4),   # Carnaval
        date(2025, 4, 18),                    # Sexta-feira Santa
        date(2025, 6, 19),                    # Corpus Christi
    ],
    2026: [
        date(2026, 2, 16), date(2026, 2, 17), # Carnaval
        date(2026, 4, 3),                     # Sexta-feira Santa
        date(2026, 6, 4),                     # Corpus Christi
    ],
    2027: [
        date(2027, 2, 8), date(2027, 2, 9),   # Carnaval
        date(2027, 3, 26),                    # Sexta-feira Santa
        date(2027, 5, 27),                    # Corpus Christi
    ],
    2028: [
        date(2028, 2, 28), date(2028, 2, 29), # Carnaval
        date(2028, 4, 14),                    # Sexta-feira Santa
        date(2028, 6, 15),                    # Corpus Christi
    ],
}


def eh_dia_util(d: date) -> bool:
    """Verifica se a data cai em dia útil (segunda a sexta) e não é feriado."""
    if d.weekday() >= 5:  # 5 = Sábado, 6 = Domingo
        return False
    
    # Checa feriados fixos
    if (d.month, d.day) in FERIADOS_FIXOS:
        return False
        
    # Checa feriados móveis
    moveis = FERIADOS_MOVEIS_POR_ANO.get(d.year, [])
    if d in moveis:
        return False
        
    return True


def subtrair_dias_uteis(data_referencia: date, dias_uteis: int) -> date:
    """
    Subtrai regressivamente N dias úteis a partir de uma data de referência (Backward Scheduling).
    """
    atual = data_referencia
    dias_restantes = int(math.ceil(dias_uteis))
    
    while dias_restantes > 0:
        atual -= timedelta(days=1)
        if eh_dia_util(atual):
            dias_restantes -= 1
            
    return atual


def somar_dias_uteis(data_inicio: date, dias_uteis: int) -> date:
    """
    Soma progressivamente N dias úteis a partir de uma data de início.
    """
    atual = data_inicio
    dias_restantes = int(math.ceil(dias_uteis))
    
    while dias_restantes > 0:
        atual += timedelta(days=1)
        if eh_dia_util(atual):
            dias_restantes -= 1
            
    return atual


def identificar_config_modalidade(modalidade: str) -> Dict[str, Any]:
    """
    Localiza as configurações da modalidade no catálogo das 10 esteiras da GCC.
    """
    m_str = str(modalidade).upper().strip()
    if modalidade in MODALIDADES_GCC_CONFIG:
        return MODALIDADES_GCC_CONFIG[modalidade]
    elif m_str in MODALIDADES_GCC_CONFIG:
        return MODALIDADES_GCC_CONFIG[m_str]
    elif 'CURSO' in m_str:
        return MODALIDADES_GCC_CONFIG['INEXIGIBILIDADE_CURSOS']
    elif 'COMPARTILH' in m_str:
        return MODALIDADES_GCC_CONFIG['INEXIGIBILIDADE_COMPARTILHAMENTO']
    elif 'INEXIGIBILIDADE' in m_str or 'INEX' in m_str:
        return MODALIDADES_GCC_CONFIG['INEXIGIBILIDADE_GERAL']
    elif 'LOCA' in m_str:
        return MODALIDADES_GCC_CONFIG['DISPENSA_LOCACAO']
    elif 'ENERGIA' in m_str:
        return MODALIDADES_GCC_CONFIG['DISPENSA_ENERGIA']
    elif 'ELET' in m_str or 'COMPRASNET' in m_str:
        return MODALIDADES_GCC_CONFIG['DISPENSA_ELETRONICA']
    elif 'BAIXO' in m_str:
        return MODALIDADES_GCC_CONFIG['DISPENSA_BAIXO_VALOR']
    elif 'AFASTAMENTO' in m_str:
        return MODALIDADES_GCC_CONFIG['AFASTAMENTO']
    elif 'PREG' in m_str:
        return MODALIDADES_GCC_CONFIG['PREGAO']
    else:
        return MODALIDADES_GCC_CONFIG['DISPENSA_TRADICIONAL']


def determinar_quadrimestre(data_obj: date) -> Dict[str, Any]:
    """
    Determina o quadrimestre regimental da Telebras (Q1, Q2, Q3) e suas datas de fechamento.
    Q1: Jan - Abr (Fechamento em 30/04)
    Q2: Mai - Ago (Fechamento em 31/08)
    Q3: Set - Dez (Fechamento em 31/12)
    """
    m = data_obj.month
    ano = data_obj.year
    if m <= 4:
        q_num = 1
        nome = f'Q1/{ano}'
        limite_apuracao = date(ano, 4, 30)
        descricao = '1º Quadrimestre (Janeiro a Abril)'
    elif m <= 8:
        q_num = 2
        nome = f'Q2/{ano}'
        limite_apuracao = date(ano, 8, 31)
        descricao = '2º Quadrimestre (Maio a Agosto)'
    else:
        q_num = 3
        nome = f'Q3/{ano}'
        limite_apuracao = date(ano, 12, 31)
        descricao = '3º Quadrimestre (Setembro a Dezembro)'
        
    return {
        'quadrimestre_codigo': nome,
        'quadrimestre_numero': q_num,
        'ano': ano,
        'descricao': descricao,
        'data_fechamento_apuracao': limite_apuracao.strftime('%Y-%m-%d')
    }


def calcular_cronograma_reverso(
    modalidade: str,
    data_pretendida_assinatura: Any,
    dias_elaboracao_etp: int = 15,
    data_hoje: Optional[date] = None
) -> Dict[str, Any]:
    """
    Calcula regressivamente a data limite de envio à GCC e a data fatal de autuação no SIGA.
    """
    if data_hoje is None:
        data_hoje = date.today()
        
    if isinstance(data_pretendida_assinatura, str):
        try:
            data_assinatura = datetime.strptime(data_pretendida_assinatura, '%Y-%m-%d').date()
        except Exception:
            data_assinatura = data_hoje + timedelta(days=180)
    elif isinstance(data_pretendida_assinatura, datetime):
        data_assinatura = data_pretendida_assinatura.date()
    elif isinstance(data_pretendida_assinatura, date):
        data_assinatura = data_pretendida_assinatura
    else:
        data_assinatura = data_hoje + timedelta(days=180)
        
    cfg = identificar_config_modalidade(modalidade)
    # Motor Estatístico de Inferência (Opção B): Grau de Confiança de 99% e Margem de Erro <= 2%
    stats_99 = calcular_estatisticas_modalidade_99(
        modalidade_key=cfg['codigo'],
        dias_etp_tr=dias_elaboracao_etp,
        dias_entrega_fornecedor=10,
        data_base=data_hoje
    )
    sla_gcc_dias = stats_99['media_dias_uteis_arredondada'] # Duração realista (ex: 31d para Pregão em vez de 144d)
    sla_planilha_antiga = cfg['prazo_gcc']
    
    # 1. Data-Limite de Envio do ETP/TR saneado à GCC
    data_limite_gcc = subtrair_dias_uteis(data_assinatura, sla_gcc_dias)
    
    # 2. Data Fatal de Abertura do Processo no SIGA pela Área
    data_fatal_siga = subtrair_dias_uteis(data_limite_gcc, dias_elaboracao_etp)
    
    # 3. Diagnóstico de Viabilidade e Risco
    quadrimestre_info = determinar_quadrimestre(data_assinatura)
    
    dias_corridos_ate_siga = (data_fatal_siga - data_hoje).days
    eh_retroativo = data_fatal_siga < data_hoje
    
    if eh_retroativo:
        dias_em_atraso = (data_hoje - data_fatal_siga).days
        classificacao_risco = 'URGÊNCIA FABRICADA / INÉRCIA DA ÁREA'
        status_viabilidade = 'INVIÁVEL'
        cor_semaforo = 'VERMELHO'
        recomendacao = (
            f'Atenção Crítica: Para assinar em {data_assinatura.strftime("%d/%m/%Y")}, o processo '
            f'deveria ter sido autuado no SIGA há {dias_em_atraso} dias atrás ({data_fatal_siga.strftime("%d/%m/%Y")}). '
            f'Esta contratação viola o rito regimental da GCC ({sla_gcc_dias} dias úteis). '
            f'Selecione uma das Janelas Cabíveis sugeridas pelo Robô de Planejamento.'
        )
    elif dias_corridos_ate_siga <= 10:
        dias_em_atraso = 0
        classificacao_risco = 'PRAZO LIMÍTROFE / RISCO ALTO'
        status_viabilidade = 'ATENÇÃO'
        cor_semaforo = 'AMARELO'
        recomendacao = (
            f'Prazo de abertura no SIGA muito próximo ({data_fatal_siga.strftime("%d/%m/%Y")}). '
            f'A área demandante deve autuar o processo e emitir a Certidão do PLAC imediatamente para evitar atraso.'
        )
    else:
        dias_em_atraso = 0
        classificacao_risco = 'PLANEJADO / REGULAR'
        status_viabilidade = 'VIÁVEL'
        cor_semaforo = 'VERDE'
        recomendacao = (
            f'Cronograma perfeitamente alinhado com a diretriz da GCC. '
            f'Abertura formal no SIGA deve ocorrer até {data_fatal_siga.strftime("%d/%m/%Y")}.'
        )
        
    return {
        'modalidade_codigo': cfg['codigo'],
        'modalidade_nome': cfg['nome'],
        'amparo_legal': cfg['amparo'],
        'sla_regimental_gcc_dias_uteis': sla_gcc_dias,
        'prazo_planilha_antigo_gcc': sla_planilha_antiga,
        'responsaveis_gcc': stats_99.get('responsaveis_gcc', 'Marcus / Layllah'),
        'ganho_eficiencia_folga_dias': sla_planilha_antiga - sla_gcc_dias,
        'grau_confianca_pct': 99.0,
        'z_score': 2.576,
        'margem_erro_pct': stats_99['margem_erro_pct'],
        'ic_99': stats_99['ic_99'],
        'cenarios': stats_99['cenarios'],
        'previsao_entrega_local': stats_99['previsao_entrega_local'],
        'dias_reserva_etp_dias_uteis': dias_elaboracao_etp,
        'total_dias_uteis_necessarios': sla_gcc_dias + dias_elaboracao_etp,
        'data_pretendida_assinatura': data_assinatura.strftime('%Y-%m-%d'),
        'data_limite_envio_gcc': data_limite_gcc.strftime('%Y-%m-%d'),
        'data_fatal_abertura_siga': data_fatal_siga.strftime('%Y-%m-%d'),
        'quadrimestre_alvo': quadrimestre_info['quadrimestre_codigo'],
        'quadrimestre_detalhe': quadrimestre_info,
        'status_viabilidade': status_viabilidade,
        'cor_semaforo': cor_semaforo,
        'classificacao_risco': classificacao_risco,
        'eh_retroativo': eh_retroativo,
        'dias_em_atraso': dias_em_atraso,
        'recomendacao_planejamento': recomendacao
    }


def verificar_capacidade_gcc(
    data_alvo: Any,
    modalidade: str = 'PREGAO',
    limiar_maximo_simultaneo: int = 8
) -> Dict[str, Any]:
    """
    Apurar a capacidade de carga da GCC na janela temporal de destino.
    Avalia a quantidade de certames cadastrados no mesmo mês/quadrimestre.
    """
    if isinstance(data_alvo, str):
        try:
            d_obj = datetime.strptime(data_alvo, '%Y-%m-%d').date()
        except Exception:
            d_obj = date.today()
    elif isinstance(data_alvo, datetime):
        d_obj = data_alvo.date()
    elif isinstance(data_alvo, date):
        d_obj = data_alvo
    else:
        d_obj = date.today()
        
    ano = d_obj.year
    mes = d_obj.month
    q_info = determinar_quadrimestre(d_obj)
    
    total_certames_janela = 0
    try:
        from .models import Demand
        total_certames_janela = Demand.objects.filter(
            intended_date__year=ano,
            intended_date__month=mes
        ).exclude(status='DEVOLVIDO_AJUSTES').count()
    except Exception:
        total_certames_janela = 0
        
    vagas_restantes = max(0, limiar_maximo_simultaneo - total_certames_janela)
    taxa_ocupacao_pct = round((total_certames_janela / limiar_maximo_simultaneo) * 100.0, 1) if limiar_maximo_simultaneo > 0 else 100.0
    
    if total_certames_janela < 6:
        status_capacidade = 'DISPONIVEL'
        cor_capacidade = 'VERDE'
        mensagem = (
            f'A GCC possui capacidade operacional desimpedida ({total_certames_janela}/{limiar_maximo_simultaneo} certames). '
            f'Restam {vagas_restantes} vagas para novas contratações neste período ({d_obj.strftime("%m/%Y")}).'
        )
    elif total_certames_janela <= limiar_maximo_simultaneo:
        status_capacidade = 'ATENCAO'
        cor_capacidade = 'AMARELO'
        mensagem = (
            f'Janela em pré-saturação na GCC ({total_certames_janela}/{limiar_maximo_simultaneo} certames previstos). '
            f'Risco de concorrência com certames de alta complexidade. Restam apenas {vagas_restantes} vaga(s).'
        )
    else:
        status_capacidade = 'SOBRECARGA'
        cor_capacidade = 'VERMELHO'
        mensagem = (
            f'Janela sobrecarregada na GCC ({total_certames_janela}/{limiar_maximo_simultaneo} certames previstos). '
            f'O acréscimo de nova demanda neste mês causará estrangulamento da equipe de compras. '
            f'Recomenda-se alocar no próximo mês ou quadrimestre.'
        )
        
    return {
        'ano': ano,
        'mes': mes,
        'mes_nome': d_obj.strftime('%m/%Y'),
        'quadrimestre': q_info['quadrimestre_codigo'],
        'total_certames_janela': total_certames_janela,
        'limiar_maximo_simultaneo': limiar_maximo_simultaneo,
        'vagas_restantes': vagas_restantes,
        'taxa_ocupacao_pct': min(100.0, taxa_ocupacao_pct),
        'status_capacidade': status_capacidade,
        'cor_capacidade': cor_capacidade,
        'mensagem_capacidade': mensagem
    }


def obter_janelas_cabiveis(
    modalidade: str = 'PREGAO',
    quantidade_sugestoes: int = 3,
    data_base: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Encontra as próximas datas e quadrimestres ideais no Calendário de Contratações
    garantindo que o rito regimental da GCC seja integralmente cumprido sem gerar urgência retroativa.
    """
    if data_base is None:
        data_base = date.today()
        
    cfg = identificar_config_modalidade(modalidade)
    sla_total_dias_uteis = cfg['prazo_gcc'] + 15
    
    primeira_data_possivel = somar_dias_uteis(data_base, sla_total_dias_uteis)
    
    sugestoes = []
    cursor_data = primeira_data_possivel
    
    while len(sugestoes) < quantidade_sugestoes:
        cronograma = calcular_cronograma_reverso(modalidade, cursor_data, data_hoje=data_base)
        capacidade = verificar_capacidade_gcc(cursor_data, modalidade)
        
        if not cronograma['eh_retroativo']:
            sugestoes.append({
                'data_sugerida_assinatura': cursor_data.strftime('%Y-%m-%d'),
                'data_formatada': cursor_data.strftime('%d/%m/%Y'),
                'quadrimestre': cronograma['quadrimestre_alvo'],
                'data_fatal_abertura_siga': cronograma['data_fatal_abertura_siga'],
                'data_limite_envio_gcc': cronograma['data_limite_envio_gcc'],
                'dias_para_abertura_siga': (datetime.strptime(cronograma['data_fatal_abertura_siga'], '%Y-%m-%d').date() - data_base).days,
                'status_capacidade': capacidade['status_capacidade'],
                'cor_capacidade': capacidade['cor_capacidade'],
                'vagas_restantes': capacidade['vagas_restantes'],
                'justificativa': (
                    f'Permite {cronograma["sla_regimental_gcc_dias_uteis"]} dias úteis de tramitação na GCC '
                    f'com autuação tranquila no SIGA até {cronograma["data_fatal_abertura_siga"]}.'
                )
            })
            
        cursor_data = somar_dias_uteis(cursor_data, 21)
        
    return sugestoes
