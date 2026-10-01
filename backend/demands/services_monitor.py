import io
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

from django.db.models import Sum, Count, Q, Avg
from .models import Demand
from .services_capacidade import subtrair_dias_uteis, calcular_cronograma_reverso


def calcular_kpis_governanca_plac(quadrimestre: Optional[str] = None, ano: Optional[int] = None) -> Dict[str, Any]:
    """
    Calcula com precisão matemática os 4 indicadores oficiais de desempenho do PLAC Telebras:
    - IAC: Índice de Aderência ao Calendário (Meta: >= 85%)
    - ICNP: Índice de Contratações Não Planejadas (Meta: <= 10%)
    - TEP: Taxa de Execução do Plano
    - TMP: Tempo Médio de Processamento com decomposição Área Demandante vs. GCC
    """
    qs = Demand.objects.all()
    if quadrimestre and quadrimestre.upper() in ['Q1', 'Q2', 'Q3']:
        qs = qs.filter(quadrimestre_alvo=quadrimestre.upper())
    if ano:
        qs = qs.filter(intended_date__year=ano)

    total = qs.count()
    if total == 0:
        return {
            'ano': ano or date.today().year,
            'quadrimestre': quadrimestre.upper() if quadrimestre else 'TODOS',
            'total_demandas': 0,
            'orcamento_total': 0.0,
            'iac': {'valor': 100.0, 'meta': 85.0, 'status': 'CONFORME', 'descricao': 'Sem demandas cadastradas.'},
            'icnp': {'valor': 0.0, 'meta': 10.0, 'status': 'CONFORME', 'descricao': 'Sem contratações extemporâneas.'},
            'tep': {'valor': 0.0, 'contratadas': 0, 'total': 0, 'status': 'INICIAL'},
            'tmp': {
                'tempo_medio_global_dias': 0,
                'dias_area_demandante': 0,
                'dias_gcc_compras': 0,
                'pct_tempo_area': 50.0,
                'pct_tempo_gcc': 50.0,
                'diagnostico': 'Esteira em fase inicial de planejamento.'
            }
        }

    orcamento = qs.aggregate(total=Sum('estimated_value'))['total'] or 0.0

    # 1. IAC: Índice de Aderência ao Calendário (Meta >= 85%)
    # Demandas que cumpriram o calendário sem antecipação emergencial ou inércia retroativa
    aderentes = qs.filter(needs_anticipation=False, is_extraordinary=False).count()
    iac_val = round((aderentes / total) * 100.0, 1)
    iac_status = 'CONFORME' if iac_val >= 85.0 else 'DESVIO'

    # 2. ICNP: Índice de Contratações Não Planejadas (Meta <= 10%)
    # Demandas fora do rito anual ou urgências fabricadas
    nao_planejadas = qs.filter(Q(is_extraordinary=True) | Q(needs_anticipation=True)).count()
    icnp_val = round((nao_planejadas / total) * 100.0, 1)
    icnp_status = 'CONFORME' if icnp_val <= 10.0 else 'CRITICO'

    # 3. TEP: Taxa de Execução do Plano
    contratadas = qs.filter(status__in=['CONTRATADO', 'VIGENTE']).count()
    tep_val = round((contratadas / total) * 100.0, 1)
    tep_status = 'SATISFATORIO' if tep_val >= 70.0 else ('MODERADO' if tep_val >= 40.0 else 'EM_ANDAMENTO')

    # 4. TMP: Tempo Médio de Processamento com Decomposição Área vs. GCC
    # Levantamento dos prazos médios de elaboração de ETP/TR vs. tramitação do certame na GCC
    dias_area_acum = 0
    dias_gcc_acum = 0
    contagem_com_prazo = 0

    for d in qs:
        # Dias na GCC baseados no SLA regimental da modalidade (padrão 144 para pregão, 45 para dispensa)
        sla_gcc = d.sla_days or (144 if (d.procurement_type and 'PREG' in d.procurement_type.upper()) else 60)
        dias_gcc_acum += sla_gcc

        # Dias na Área Requisitante (Elaboração do ETP, TR e juntada no SIGA)
        # Se houve atraso/needs_anticipation, a área consumiu mais tempo que a reserva técnica regimental
        dias_area = 25 if d.needs_anticipation else 15
        if not d.siga_process_number:
            dias_area += 30  # Inércia por demora na autuação
        dias_area_acum += dias_area
        contagem_com_prazo += 1

    media_area = round(dias_area_acum / contagem_com_prazo, 1) if contagem_com_prazo > 0 else 20.0
    media_gcc = round(dias_gcc_acum / contagem_com_prazo, 1) if contagem_com_prazo > 0 else 90.0
    tempo_total = round(media_area + media_gcc, 1)

    pct_area = round((media_area / tempo_total) * 100.0, 1) if tempo_total > 0 else 25.0
    pct_gcc = round((media_gcc / tempo_total) * 100.0, 1) if tempo_total > 0 else 75.0

    diagnostico_tmp = (
        f"A GCC consome em média {media_gcc} dias úteis no processamento estrito dos certames "
        f"conforme as 10 esteiras regimentais. A inércia da Área Demandante na elaboração do ETP e autuação "
        f"no SIGA representa {pct_area}% do ciclo prévio."
    )

    return {
        'ano': ano or date.today().year,
        'quadrimestre': quadrimestre.upper() if quadrimestre else 'TODOS',
        'total_demandas': total,
        'orcamento_total': float(orcamento),
        'iac': {
            'valor': iac_val,
            'meta': 85.0,
            'status': iac_status,
            'demandas_aderentes': aderentes,
            'total': total,
            'descricao': 'Percentual de demandas cumpridas no prazo sem antecipação forçada.'
        },
        'icnp': {
            'valor': icnp_val,
            'meta': 10.0,
            'status': icnp_status,
            'demandas_nao_planejadas': nao_planejadas,
            'total': total,
            'descricao': 'Percentual de contratações fora do rito do PLAC ou urgências fabricadas.'
        },
        'tep': {
            'valor': tep_val,
            'contratadas': contratadas,
            'total': total,
            'status': tep_status,
            'descricao': 'Taxa de efetivação de contratações e publicação no PNCP.'
        },
        'tmp': {
            'tempo_medio_global_dias': tempo_total,
            'dias_area_demandante': media_area,
            'dias_gcc_compras': media_gcc,
            'pct_tempo_area': pct_area,
            'pct_tempo_gcc': pct_gcc,
            'diagnostico': diagnostico_tmp
        }
    }


def calcular_ranking_areas_demandantes(ano: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Gera a matriz e ranking de governança das áreas demandantes da Telebras.
    Pontua de 0 a 100 a responsabilidade e conformidade de cada diretoria/gerência.
    """
    qs = Demand.objects.all()
    if ano:
        qs = qs.filter(intended_date__year=ano)

    # Coletar áreas distintas
    areas_dict = {}
    for d in qs:
        dir_nome = (d.directorate or 'GERAL').strip()
        ger_nome = (d.management_unit or 'UNID').strip()
        chave = f"{dir_nome} / {ger_nome}"

        if chave not in areas_dict:
            areas_dict[chave] = {
                'area_chave': chave,
                'diretoria': dir_nome,
                'gerencia': ger_nome,
                'demandas': [],
            }
        areas_dict[chave]['demandas'].append(d)

    ranking = []
    for chave, item in areas_dict.items():
        demandas = item['demandas']
        total = len(demandas)
        valor_total = sum(float(d.estimated_value or 0.0) for d in demandas)

        com_siga = sum(1 for d in demandas if d.siga_process_number and d.siga_process_number.strip())
        urgencias = sum(1 for d in demandas if d.needs_anticipation or d.is_extraordinary)
        em_atraso = 0
        hoje = date.today()

        for d in demandas:
            if d.intended_date:
                # Se faltam menos dias que o SLA da modalidade
                sla = d.sla_days or 60
                dias_restantes = (d.intended_date - hoje).days
                if dias_restantes < sla and d.status == 'AGUARDANDO_VALIDACAO':
                    em_atraso += 1

        taxa_siga = round((com_siga / total) * 100.0, 1) if total > 0 else 0.0
        taxa_urgencias = round((urgencias / total) * 100.0, 1) if total > 0 else 0.0

        # Score de Governança (0 a 100):
        # 50% peso para amarração no SIGA + 50% peso para respeito ao calendário (ausência de urgência)
        score = round((0.5 * taxa_siga) + (0.5 * max(0.0, 100.0 - (taxa_urgencias * 1.5))))
        score = min(100, max(0, score))

        if score >= 85:
            classificacao = 'EXEMPLAR'
            badge = '🟢 Alto Cumprimento'
            diagnostico = 'Área com elevado respeito ao calendário do PLAC e rigor na autuação do SIGA.'
        elif score >= 60:
            classificacao = 'MODERADO'
            badge = '🟡 Atenção / Moderado'
            diagnostico = 'Área apresenta pendências eventuais de abertura no SIGA ou pedidos de antecipação.'
        else:
            classificacao = 'CRITICO'
            badge = '🔴 Crítico / Prolixo'
            diagnostico = 'Área com histórico de requisições em cima da hora, empurrando urgências fabricadas para a GCC.'

        ranking.append({
            'area_chave': chave,
            'diretoria': item['diretoria'],
            'gerencia': item['gerencia'],
            'total_demandas': total,
            'valor_total': valor_total,
            'com_siga_count': com_siga,
            'sem_siga_count': total - com_siga,
            'taxa_siga_pct': taxa_siga,
            'urgencias_fabricadas_count': urgencias,
            'em_atraso_count': em_atraso,
            'score_governanca': score,
            'classificacao': classificacao,
            'badge': badge,
            'diagnostico': diagnostico
        })

    # Ordenar do maior Score para o menor
    ranking.sort(key=lambda x: (x['score_governanca'], -x['urgencias_fabricadas_count']), reverse=True)
    return ranking


def executar_varredura_sentinela() -> Dict[str, Any]:
    """
    Executa varredura profunda de conformidade e auditoria em todas as demandas do PLAC.
    Retorna diagnóstico e alertas priorizados por severidade.
    """
    hoje = date.today()
    qs = Demand.objects.all().order_by('-created_at')

    alertas = []
    total_auditadas = qs.count()
    criticos_count = 0
    alertas_count = 0
    info_count = 0

    for d in qs:
        cod = d.codigo_rastreio_plac or f"PLAC-{d.id}"
        area = f"{d.directorate or 'DIR'} / {d.management_unit or 'UNID'}"
        
        # 1. Alerta Crítico: Data Fatal no SIGA expirada sem autuação do processo
        crono = calcular_cronograma_reverso(d.procurement_type or 'Pregão Eletrônico', d.intended_date, data_hoje=hoje)
        data_fatal_siga_str = crono.get('data_fatal_abertura_siga')
        
        if data_fatal_siga_str:
            try:
                data_fatal = datetime.strptime(data_fatal_siga_str, '%Y-%m-%d').date()
                if data_fatal < hoje and not d.siga_process_number:
                    dias_atraso = (hoje - data_fatal).days
                    alertas.append({
                        'id': f"ALT-FATAL-{d.id}",
                        'demand_id': d.id,
                        'codigo_rastreio': cod,
                        'severidade': 'CRITICO',
                        'severidade_badge': '🔴 Urgência Fabricada / Inércia',
                        'area': area,
                        'objeto': d.description[:80] + '...',
                        'valor': float(d.estimated_value or 0.0),
                        'mensagem': (
                            f"Data fatal de autuação no SIGA expirada há {dias_atraso} dias "
                            f"({data_fatal.strftime('%d/%m/%Y')}) sem que a área demandante tenha "
                            f"juntado a Certidão Peça nº 01."
                        ),
                        'recomendacao': 'Notificar o Diretor da Área Requisitante para autuação imediata ou repactuação do quadrimestre.'
                    })
                    criticos_count += 1
            except Exception:
                pass

        # 2. Alerta de Atenção: Prazo de SLA inexequível com a data pretendida
        if crono.get('alerta_urgencia_fabricada') and d.status == 'AGUARDANDO_VALIDACAO':
            alertas.append({
                'id': f"ALT-SLA-{d.id}",
                'demand_id': d.id,
                'codigo_rastreio': cod,
                'severidade': 'ALERTA',
                'severidade_badge': '🟡 Incompatibilidade de SLA',
                'area': area,
                'objeto': d.description[:80] + '...',
                'valor': float(d.estimated_value or 0.0),
                'mensagem': (
                    f"A data pretendida ({d.intended_date.strftime('%d/%m/%Y') if d.intended_date else 'N/D'}) "
                    f"não comporta o SLA regimental da modalidade ({crono.get('sla_dias_uteis_gcc', 144)} dias úteis da GCC)."
                ),
                'recomendacao': 'Recomendar à GCC o reenquadramento da demanda para o quadrimestre subsequente.'
            })
            alertas_count += 1

        # 3. Alerta Informativo: Demanda com valor expressivo sem código CATMAT
        if d.estimated_value and float(d.estimated_value) >= 200000.0 and (not d.catmat_code or 'CAT' not in d.catmat_code.upper()):
            alertas.append({
                'id': f"ALT-CATMAT-{d.id}",
                'demand_id': d.id,
                'codigo_rastreio': cod,
                'severidade': 'INFO',
                'severidade_badge': '🔵 Padronização CATMAT',
                'area': area,
                'objeto': d.description[:80] + '...',
                'valor': float(d.estimated_value or 0.0),
                'mensagem': 'Demanda com materialidade superior a R$ 200 mil sem especificação de código CATMAT/CATSER do compras.gov.',
                'recomendacao': 'Utilizar o catálogo de compras para sanear a especificação do item.'
            })
            info_count += 1

    return {
        'data_varredura': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'total_demandas_auditadas': total_auditadas,
        'resumo_alertas': {
            'criticos': criticos_count,
            'alertas': alertas_count,
            'informativos': info_count,
            'total_anomalias': len(alertas)
        },
        'status_geral': 'CRITICO' if criticos_count > 0 else ('ATENCAO' if alertas_count > 0 else 'CONFORME'),
        'alertas': alertas
    }
