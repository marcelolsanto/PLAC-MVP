"""
Serviço de Telemetria e Gestão da Fase de Planejamento (Kanban SIGA 2026)
Consolida processos em tramitação no SIGA vinculados a demandas do PLAC.
Removemos as planilhas locais; tudo vem do PostgreSQL via SigaProcess e Demand.
"""

from datetime import datetime
import hashlib
from typing import Dict, Any, Optional

# Parâmetros Regimentais e Médias Históricas da Telebras por Macro-Fase
KANBAN_MACRO_FASES = {
    "1_DFD": {
        "id": "1_DFD",
        "nome": "1. Autuação & DFD",
        "setor_padrao": "Área Demandante",
        "sla_dias_uteis": 10,
        "media_historica_dias": 10.5,
    },
    "2_ETP": {
        "id": "2_ETP",
        "nome": "2. ETP & Matriz de Riscos",
        "setor_padrao": "Equipe de Planejamento",
        "sla_dias_uteis": 35,
        "media_historica_dias": 37.8,
    },
    "3_PESQUISA_TR": {
        "id": "3_PESQUISA_TR",
        "nome": "3. Pesquisa de Preços & TR",
        "setor_padrao": "Demandante / Apoio GCC",
        "sla_dias_uteis": 20,
        "media_historica_dias": 25.3,
    },
    "4_JURIDICO": {
        "id": "4_JURIDICO",
        "nome": "4. Análise Jurídica & Diligências",
        "setor_padrao": "CONJUR / Gabinetes",
        "sla_dias_uteis": 15,
        "media_historica_dias": 16.9,
    },
    "5_GCC": {
        "id": "5_GCC",
        "nome": "5. Triagem & Prontidão GCC",
        "setor_padrao": "GCC / Licitações",
        "sla_dias_uteis": 10,
        "media_historica_dias": 10.5,
    }
}

RESPONSAVEIS_POR_GERENCIA = {
    "1100-GAB PR": ("1000 - Presidência", "Layse / Ascom Presidência"),
    "2600-GCC": ("2000 - Diretoria Administrativo-Financeira", "Pedro Diniz / Rosilda (GCC)"),
}

def obter_dados_kanban_planejamento(ano: int = 2026, diretoria: Optional[str] = None, risco: Optional[str] = None, busca: Optional[str] = None) -> Dict[str, Any]:
    from .models import Demand

    # Busca apenas processos ativos no SIGA que pertencem ao planejamento (Demands ativas)
    demands = Demand.objects.exclude(status__in=['CONTRATADO', 'VIGENTE']).prefetch_related('siga_processes')

    fases_chaves = list(KANBAN_MACRO_FASES.keys())
    processos = []
    
    for d in demands:
        # Se tem processo SIGA atrelado
        siga_procs = d.siga_processes.all()
        siga_proc = siga_procs.first() if siga_procs.exists() else None

        cv = d.codigo_rastreio_plac or f"REQ-{d.id}"
        ger = d.management_unit or ""
        
        # Define fase baseado no status do processo ou usa 1_DFD padrão
        stage_idx = 0
        dias_setor = 0
        num_siga = "A Autuar"
        if siga_proc:
            num_siga = siga_proc.numero_processo
            dias_setor = siga_proc.dias_na_fase
            fase_str = (siga_proc.fase_atual or "").lower()
            if "etp" in fase_str: stage_idx = 1
            elif "pesquisa" in fase_str or "tr" in fase_str: stage_idx = 2
            elif "jur" in fase_str or "conjur" in fase_str: stage_idx = 3
            elif "gcc" in fase_str or "triagem" in fase_str: stage_idx = 4

        stage_id = fases_chaves[stage_idx]
        stage_cfg = KANBAN_MACRO_FASES[stage_id]

        dir_nome, custodiante_padrao = RESPONSAVEIS_POR_GERENCIA.get(ger, (d.directorate or "Geral", "Analista Designado"))

        if stage_id == "4_JURIDICO":
            custodiante = "Dr. Fernando Rocha / Procuradoria CONJUR"
            setor_atual_sigla = "CONJUR"
            setor_atual_nome = "CONJUR - Consultoria Jurídica"
        elif stage_id == "5_GCC":
            custodiante = "Pedro Diniz / Rosilda (GCC Compras)"
            setor_atual_sigla = "GCC"
            setor_atual_nome = "2600 - Gerência de Compras e Contratos"
        else:
            custodiante = custodiante_padrao
            setor_atual_sigla = ger.split('-')[1].strip() if '-' in ger else ger
            setor_atual_nome = f"{ger} - Área Demandante"

        sla_etapa = stage_cfg["sla_dias_uteis"]
        media_etapa = stage_cfg["media_historica_dias"]
        desvio_sla = dias_setor - sla_etapa
        desvio_media = round(dias_setor - media_etapa, 1)

        # Classificação de Gargalo
        if desvio_sla > 10:
            status_prazo = "GARGALO CRÍTICO"
            status_prazo_badge = "CRITICO"
        elif desvio_sla > 0:
            status_prazo = "ATENÇÃO"
            status_prazo_badge = "ATENCAO"
        else:
            status_prazo = "NO PRAZO"
            status_prazo_badge = "NO_PRAZO"

        if desvio_media > 0:
            diff_media_str = f"+{desvio_media}d acima da média da etapa ({media_etapa}d)"
        elif desvio_media < 0:
            diff_media_str = f"{desvio_media}d abaixo da média da etapa ({media_etapa}d)"
        else:
            diff_media_str = f"Exatamente na média da etapa ({media_etapa}d)"

        # Risco
        if stage_idx <= 1 and dias_setor > 40:
            risco_nao_contratar = "ALTO RISCO"
            risco_nivel = "ALTO"
        elif stage_idx <= 2 and dias_setor > 25:
            risco_nao_contratar = "MÉDIO"
            risco_nivel = "MEDIO"
        else:
            risco_nao_contratar = "BAIXO"
            risco_nivel = "BAIXO"

        processos.append({
            "cod_verif": cv,
            "numero_siga": num_siga,
            "objeto": d.description or "Sem descrição",
            "gerencia_demandante": ger,
            "diretoria": dir_nome,
            "setor_atual_sigla": setor_atual_sigla,
            "setor_atual_nome": setor_atual_nome,
            "fase_atual_id": stage_id,
            "fase_atual_nome": stage_cfg["nome"],
            "dias_no_setor": dias_setor,
            "sla_etapa_dias": sla_etapa,
            "status_prazo": status_prazo,
            "status_prazo_badge": status_prazo_badge,
            "custodiante": custodiante,
            "diff_media_str": diff_media_str,
            "risco_nao_contratar": risco_nao_contratar,
            "risco_nivel": risco_nivel,
            "modelo_estimado": d.procurement_type or "A Definir",
            "orcamento_estimado": float(d.estimated_value or 0.0)
        })

    # Filtros
    if diretoria:
        processos = [p for p in processos if diretoria.lower() in p["diretoria"].lower()]
    if risco:
        processos = [p for p in processos if p["risco_nivel"] == risco.upper()]
    if busca:
        b = busca.lower()
        processos = [p for p in processos if b in p["cod_verif"].lower() or b in p["objeto"].lower() or b in p["numero_siga"].lower()]

    agrupados = {k: [] for k in fases_chaves}
    for p in processos:
        agrupados[p["fase_atual_id"]].append(p)

    return {
        "timestamp_atualizacao": datetime.now().isoformat(),
        "total_processos": len(processos),
        "fases": agrupados,
        "indicadores": {
            "no_prazo": len([p for p in processos if p["status_prazo_badge"] == "NO_PRAZO"]),
            "atencao": len([p for p in processos if p["status_prazo_badge"] == "ATENCAO"]),
            "critico": len([p for p in processos if p["status_prazo_badge"] == "CRITICO"]),
            "alto_risco_contratar": len([p for p in processos if p["risco_nivel"] == "ALTO"]),
        }
    }
