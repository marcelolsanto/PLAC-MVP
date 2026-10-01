import io
import hashlib
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from django.db.models import Sum, Count, Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from .models import Demand
from .services_capacidade import verificar_capacidade_gcc


# ─────────────────────────────────────────────────────────────────────────────
# Mapa de vinculação COD_VERIF da planilha PLAC 2026 por unidade/objeto
# Chave: fragmento do objeto (lowercase), Valor: cod_verif da aba BASE_PLAC_2026
# ─────────────────────────────────────────────────────────────────────────────
_COD_VERIF_MAP = {
    "cabo": "3100-GEOP_08",
    "fibra óptica": "3100-GEOP_08",
    "fibra optica": "3100-GEOP_08",
    "monomodo": "3100-GEOP_08",
    "registro de preços": "3100-GEOP_08",
    "segurança da informação": "4100-GSI_03",
    "cibersegurança": "4100-GSI_03",
    "logística": "2200-GLOG_05",
    "material de expediente": "2200-GLOG_22",
    "contabilidade": "4300-GCO_01",
    "ti": "4200-GTI_11",
    "sistemas": "4200-GTI_11",
    "licença de software": "4200-GTI_11",
    "auditoria": "4300-GCO_01",
    "energia elétrica": "2300-GAF_06",
    "limpeza": "2200-GLOG_14",
    "vigilância": "2200-GLOG_15",
    "locação de veículo": "2200-GLOG_18",
    "capacitação": "2400-GGP_09",
    "treinamento": "2400-GGP_09",
    "satellite": "3500-GORS_02",
    "satelital": "3500-GORS_02",
    "infraestrutura": "3600-GINF_04",
    "data center": "3600-GINF_04",
}

# Mapa de diagnóstico de represamento por unidade (setor_atual_sigla)
_MOTIVO_PARADO_MAP = {
    "GEOP":    "Aguardando autuação eletrônica no SIGA pela gerência de engenharia (DFD não assinado pela chefia)",
    "GPTC":    "ETP em elaboração pela equipe técnica — pesquisa de preços pendente junto ao mercado",
    "GEIN":    "Termo de Referência aguardando revisão jurídica interna da DTO antes do envio à GCC",
    "GEAT":    "DFD autuado, aguardando assinatura do Gerente para envio à DAFRI",
    "GORS":    "Pesquisa de preços em andamento com 3 fornecedores (prazo: +10 dias úteis)",
    "GINF":    "Processo autuado no SIGA — aguardando emissão da Certidão de Admissibilidade do PLAC (Peça nº 01)",
    "GCL":     "Aguardando DIF (Documento de Instrução Financeira) da GAF/SAP para amparar o valor estimado",
    "GLOG":    "DFD aprovado. ETP em revisão — falta memorial descritivo técnico das especificações do item",
    "GGP":     "Processo devolvido pela GCC para complementação do quantitativo justificado no Bloco 2",
    "GCC":     "Processo na fila da GCC para triagem. Aguardando convocação para reunião de alinhamento",
    "CONJUR":  "Diligência jurídica emitida — aguardando esclarecimentos da área sobre o enquadramento legal",
    "GAF":     "Dotação orçamentária reservada no SAP. Aguardando liberação do empenho pela GEFIN",
    "GTI":     "Sistema legado impede autuação automatizada — processo manual em curso no SIGA",
    "GAB PR":  "Demanda estratégica aguardando priorização na pauta da próxima reunião de diretoria",
    "GECAD":   "Minuta contratual em análise pelo GECAD — aguardando retorno do setor jurídico",
    "GGOV":    "Pendente de parecer de conformidade com o PCA e Regulamento de Licitações",
}

# Checklist de pendências para avançar para Validação do Diretor (por status SIGA)
def _calcular_pendencias_validacao(demand: Demand, tem_siga: bool) -> List[Dict]:
    """Retorna checklist de pendências para a demanda avançar para Validação do Diretor."""
    pendencias = []

    # Pend. 1: Autuação formal no SIGA
    pendencias.append({
        "id": "siga_autuacao",
        "descricao": "Autuação formal do processo no SIGA (TLB-PRO-XXXX/XXXXXX)",
        "concluido": tem_siga,
        "urgencia": "CRITICA" if not tem_siga else "OK",
        "instrucao": "Acesse o SIGA e crie um novo processo administrativo vinculando esta demanda ao PLAC 2026."
    })

    # Pend. 2: Certidão de Admissibilidade do PLAC
    pendencias.append({
        "id": "certidao_plac",
        "descricao": "Emissão e juntada da Certidão de Admissibilidade ao PLAC como Peça nº 01",
        "concluido": bool(demand.certidao_emitida_em),
        "urgencia": "CRITICA" if not demand.certidao_emitida_em else "OK",
        "instrucao": "Gere a Certidão via botão '📄 Certidão & SIGA' e junte ao processo SIGA como primeira peça."
    })

    # Pend. 3: DFD assinado
    dfd_assinado = bool(demand.siga_process_number)  # proxy: se tem SIGA, DFD foi juntado
    pendencias.append({
        "id": "dfd_assinado",
        "descricao": "DFD assinado pela chefia da unidade demandante e juntado ao processo",
        "concluido": dfd_assinado,
        "urgencia": "ALTA" if not dfd_assinado else "OK",
        "instrucao": "O Gestor da unidade deve assinar eletronicamente o DFD no SIGA antes do envio ao Diretor."
    })

    # Pend. 4: Código de Rastreio PLAC gerado
    pendencias.append({
        "id": "codigo_rastreio",
        "descricao": f"Código de Rastreio PLAC gerado ({demand.codigo_rastreio_plac or 'Pendente'})",
        "concluido": bool(demand.codigo_rastreio_plac),
        "urgencia": "MEDIA" if not demand.codigo_rastreio_plac else "OK",
        "instrucao": "O código é gerado automaticamente ao salvar a demanda. Verifique se o campo está preenchido."
    })

    return pendencias


def enriquecer_telemetria_levantamento(demand: Demand) -> Dict[str, Any]:
    """
    Enriquece um objeto Demand (status AGUARDANDO_VALIDACAO) com telemetria SIGA para
    exibição nos cards da coluna '1. Levantamento' do Kanban de Governança do PLAC.

    Retorna dicionário com:
    - cod_verif: código verificador da planilha PLAC 2026
    - custodiante_atual: nome do servidor/equipe atual responsável
    - setor_atual_sigla: sigla do setor onde o processo está parado
    - setor_atual_nome: nome completo do setor no SIGA
    - motivo_parado: diagnóstico textual do represamento
    - dias_no_setor: dias úteis de permanência na etapa atual
    - pendencias_validacao_diretor: lista de pendências estruturadas
    - documentos_juntados: lista de peças juntadas ao processo
    - sla_modalidade: SLA regimental em dias úteis
    - desvio_prazo: +/- em relação à média histórica
    """
    from .services_siga import PROCESSOS_SIGA_VIGENTES as PROCESSOS_SIGA_MOCK

    # ── 1. Descobrir cod_verif a partir do objeto ──────────────────────────
    descricao = (demand.description or "").lower()
    cod_verif = demand.codigo_rastreio_plac  # fallback: rastreio do sistema

    for fragmento, cod in _COD_VERIF_MAP.items():
        if fragmento in descricao:
            cod_verif = cod
            break

    # ── 2. Cross-reference com mock SIGA para obter telemetria ────────────
    siga_match = None
    for proc in PROCESSOS_SIGA_MOCK:
        obj_siga = (proc.get("objeto") or "").lower()
        val_siga = proc.get("valor_estimado", 0)
        # Matcheia por valor estimado + keywords do objeto
        val_diff = abs(float(demand.estimated_value or 0) - float(val_siga)) if val_siga else 999999
        has_keyword = any(k in obj_siga for k in descricao.split()[:4] if len(k) > 3)
        if val_diff < 50000 or has_keyword:
            siga_match = proc
            break

    # ── 3. Dados do processo SIGA (real ou sintético) ─────────────────────
    tem_siga = bool(demand.siga_process_number and str(demand.siga_process_number).strip())

    if siga_match:
        unidade_raw = siga_match.get("unidade_demandante", "")
        ger_sigla = unidade_raw.split("-")[0].strip() if "-" in unidade_raw else "AREA"
        custodiante_atual = siga_match.get("custodiante_atual", "Analista Responsável")
        setor_atual_sigla = siga_match.get("setor_atual_sigla", ger_sigla)
        setor_atual_nome = siga_match.get("setor_atual_nome", unidade_raw or "Área Demandante")
        dias_no_setor = siga_match.get("dias_no_setor", 10)
        documentos_juntados = siga_match.get("documentos", [])
        ultimo_despacho = siga_match.get("ultimo_evento_siga", "")
    else:
        # Gera dados determinísticos baseados no ID da demanda
        h = int(hashlib.md5(str(demand.id).encode()).hexdigest(), 16)
        unidades = list(_MOTIVO_PARADO_MAP.keys())
        setor_atual_sigla = unidades[h % len(unidades)]
        setor_atual_nome = f"Área Demandante / {setor_atual_sigla}"
        custodiante_atual = "Responsável Designado pela Gerência"
        dias_no_setor = 5 + (h % 25)
        documentos_juntados = []
        ultimo_despacho = "Processo aguardando instrução inicial pela área demandante."

    # Adiciona DFD mock se não há documentos juntados
    if not documentos_juntados and tem_siga:
        documentos_juntados = [
            {
                "id": "DOC-DFD-01",
                "titulo": f"DFD_{demand.description[:20].replace(' ', '_')}.pdf",
                "tipo": "PDF",
                "tamanho_kb": 185,
                "data_juntada": date.today().strftime("%Y-%m-%d"),
                "signatario": "Área Demandante",
                "resumo_conteudo": "Documento de Formalização da Demanda.",
            }
        ]

    # ── 4. Diagnóstico do represamento ────────────────────────────────────
    motivo_parado = _MOTIVO_PARADO_MAP.get(setor_atual_sigla,
        "Processo aguardando autuação formal no SIGA e assinatura do DFD pela chefia da unidade.")

    if not tem_siga:
        motivo_parado = (
            "Processo não autuado no SIGA. A área demandante precisa abrir os autos eletrônicos "
            "e juntar a Certidão de Admissibilidade do PLAC como Peça nº 01 antes do envio ao Diretor."
        )

    # ── 5. SLA e desvio ───────────────────────────────────────────────────
    procurement = (demand.procurement_type or "PREGAO").upper()
    if "PREG" in procurement:
        sla_modalidade = demand.sla_days or 150
    elif "DISPENSA" in procurement or "DISP" in procurement:
        sla_modalidade = demand.sla_days or 60
    elif "INEX" in procurement:
        sla_modalidade = demand.sla_days or 45
    else:
        sla_modalidade = demand.sla_days or 90

    # Média histórica DFD/Levantamento: 15 dias úteis
    media_levantamento = 15
    desvio_prazo = dias_no_setor - media_levantamento
    desvio_str = f"+{desvio_prazo}d" if desvio_prazo >= 0 else f"{desvio_prazo}d"
    status_prazo = "CRITICO" if desvio_prazo > 10 else ("ATENCAO" if desvio_prazo > 0 else "OK")

    # ── 6. Checklist de pendências ────────────────────────────────────────
    pendencias = _calcular_pendencias_validacao(demand, tem_siga)

    return {
        "cod_verif": cod_verif or f"PLAC-{demand.directorate or 'N/D'}",
        "custodiante_atual": custodiante_atual,
        "setor_atual_sigla": setor_atual_sigla,
        "setor_atual_nome": setor_atual_nome,
        "motivo_parado": motivo_parado,
        "dias_no_setor": dias_no_setor,
        "sla_modalidade": sla_modalidade,
        "desvio_prazo": desvio_prazo,
        "desvio_str": desvio_str,
        "status_prazo": status_prazo,
        "pendencias_validacao_diretor": pendencias,
        "documentos_juntados": documentos_juntados,
        "ultimo_despacho_siga": ultimo_despacho,
        "tem_siga": tem_siga,
        "total_pendencias": sum(1 for p in pendencias if not p["concluido"]),
    }


def obter_resumo_esteira(quadrimestre: Optional[str] = None, ano: Optional[int] = None) -> Dict[str, Any]:
    """
    Consolida as métricas da Esteira de Governança do PLAC:
    - Contagem por fase do funil
    - Orçamento total
    - Semáforo de capacidade da GCC no quadrimestre/ano
    - Identificação de urgências fabricadas e pendências de SIGA
    """
    qs = Demand.objects.all()
    if quadrimestre and quadrimestre.upper() in ['Q1', 'Q2', 'Q3']:
        qs = qs.filter(quadrimestre_alvo=quadrimestre.upper())
    if ano:
        qs = qs.filter(intended_date__year=ano)

    total_demandas = qs.count()
    orcamento_total = qs.aggregate(total=Sum('estimated_value'))['total'] or 0.0

    # Contagens por etapa
    fases = {
        'levantamento': qs.filter(status='AGUARDANDO_VALIDACAO').count(),
        'validacao_diretor': qs.filter(status='VALIDADO_DIRETOR').count(),
        'consolidacao_gcc': qs.filter(status='CONSOLIDADO').count(),
        'deliberacao_redir': qs.filter(status='DELIBERACAO_REDIR').count(),
        'calendario_vigente': qs.filter(status__in=['CONTRATADO', 'VIGENTE']).count(),
        'devolvido_ajustes': qs.filter(status='DEVOLVIDO_AJUSTES').count(),
    }

    # Demandas pendentes de vinculação do processo SIGA
    sem_siga_count = qs.filter(
        Q(siga_process_number__isnull=True) | Q(siga_process_number__exact='')
    ).count()

    # Urgências Fabricadas (alertadas pela regressão de capacidade ou prazos vencidos)
    urgencias_fabricadas_count = qs.filter(
        Q(needs_anticipation=True) | Q(is_extraordinary=True)
    ).count()

    # Semáforo de Capacidade Operacional da GCC
    ano_ref = ano or date.today().year
    if quadrimestre and quadrimestre.upper() == 'Q1':
        data_alvo = date(ano_ref, 3, 15)
    elif quadrimestre and quadrimestre.upper() == 'Q2':
        data_alvo = date(ano_ref, 7, 15)
    elif quadrimestre and quadrimestre.upper() == 'Q3':
        data_alvo = date(ano_ref, 11, 15)
    else:
        data_alvo = date(ano_ref, date.today().month, 1)

    capacidade_gcc = verificar_capacidade_gcc(data_alvo=data_alvo)

    return {
        'ano': ano_ref,
        'quadrimestre': quadrimestre.upper() if quadrimestre else 'TODOS',
        'total_demandas': total_demandas,
        'orcamento_total': float(orcamento_total),
        'fases': fases,
        'sem_siga_count': sem_siga_count,
        'urgencias_fabricadas_count': urgencias_fabricadas_count,
        'capacidade_gcc': capacidade_gcc
    }


def gerar_minuta_consolidada_pdf(quadrimestre: Optional[str] = None, ano: Optional[int] = None) -> bytes:
    """
    Renderiza em PDF paisagem o Relatório Consolidado do PLAC para instrução
    e deliberação oficial da REDIR e parecer técnico da DAFRI.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=25,
        leftMargin=25,
        topMargin=25,
        bottomMargin=25
    )

    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )
    
    style_subtitle = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    )

    style_th = ParagraphStyle(
        'TableHead',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.white
    )

    style_td = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        alignment=TA_LEFT,
        textColor=colors.HexColor('#1e293b')
    )

    style_td_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e293b')
    )

    style_td_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )

    elements = []

    # Cabeçalho Oficial
    elements.append(Paragraph("TELECOMUNICAÇÕES BRASILEIRAS S.A. — TELEBRAS", style_title))
    elements.append(Paragraph("DIRETORIA DE ADMINISTRAÇÃO, FINANÇAS E RELAÇÕES COM INVESTIDORES — DAFRI", style_subtitle))
    elements.append(Paragraph("GERÊNCIA DE COMPRAS E CONTRATOS — GCC", style_subtitle))
    elements.append(Spacer(1, 8))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=10))

    # Título do Relatório
    quad_label = f"QUADRIMESTRE: {quadrimestre.upper()}" if quadrimestre else "CICLO CONSOLIDADO (TODOS OS QUADRIMESTRES)"
    ano_label = f"EXERCÍCIO {ano or date.today().year}"
    elements.append(Paragraph(f"<b>MINUTA CONSOLIDADA DO PLANO ANUAL DE CONTRATAÇÕES (PLAC)</b>", style_title))
    elements.append(Paragraph(f"{ano_label} — {quad_label} | PROCESSO DE DELIBERAÇÃO REDIR", style_subtitle))
    elements.append(Spacer(1, 12))

    # Buscar Demandas Aprovadas / Consolidadas
    qs = Demand.objects.all().order_by('intended_date', 'id')
    if quadrimestre and quadrimestre.upper() in ['Q1', 'Q2', 'Q3']:
        qs = qs.filter(quadrimestre_alvo=quadrimestre.upper())
    if ano:
        qs = qs.filter(intended_date__year=ano)

    total_demandas = qs.count()
    orcamento_total = qs.aggregate(total=Sum('estimated_value'))['total'] or 0.0

    # Tabela Resumo Executivo
    resumo_data = [
        [
            Paragraph("<b>Total de Demandas</b>", style_th),
            Paragraph("<b>Valor Global Estimado</b>", style_th),
            Paragraph("<b>Data de Fechamento</b>", style_th),
            Paragraph("<b>Finalidade do Documento</b>", style_th)
        ],
        [
            Paragraph(f"<b>{total_demandas} demandas</b>", style_td_center),
            Paragraph(f"<b>R$ {orcamento_total:,.2f}</b>", style_td_center),
            Paragraph(datetime.now().strftime("%d/%m/%Y %H:%M"), style_td_center),
            Paragraph("Subsidiar a deliberação colegiada da Diretoria Executiva (Ata REDIR)", style_td_center)
        ]
    ]
    t_resumo = Table(resumo_data, colWidths=[130, 160, 150, 310])
    t_resumo.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8fafc')),
    ]))
    elements.append(t_resumo)
    elements.append(Spacer(1, 14))

    # Tabela Detalhada de Demandas
    elements.append(Paragraph("<b>RELAÇÃO OFICIAL DE DEMANDAS CONSOLIDADAS:</b>", ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor('#0f172a'))))
    elements.append(Spacer(1, 4))

    table_data = [
        [
            Paragraph("<b>Item</b>", style_th),
            Paragraph("<b>Cód. PLAC</b>", style_th),
            Paragraph("<b>Proc. SIGA</b>", style_th),
            Paragraph("<b>Área / Gerência</b>", style_th),
            Paragraph("<b>Descrição do Objeto</b>", style_th),
            Paragraph("<b>Modalidade</b>", style_th),
            Paragraph("<b>SLA</b>", style_th),
            Paragraph("<b>Data Pretendida</b>", style_th),
            Paragraph("<b>Valor Estimado (R$)</b>", style_th),
            Paragraph("<b>Status</b>", style_th),
        ]
    ]

    for idx, d in enumerate(qs, 1):
        cod_plac = d.codigo_rastreio_plac or f"PLAC-{d.id}"
        proc_siga = d.siga_process_number or "— PENDENTE —"
        area = f"{d.directorate or 'DIR'} / {d.management_unit or 'UNID'}"
        desc = (d.description[:65] + '...') if len(d.description) > 65 else d.description
        mod = d.procurement_type or "A DEFINIR"
        sla = f"{d.sla_days} d.u." if d.sla_days else "—"
        data_p = d.intended_date.strftime("%d/%m/%Y") if d.intended_date else "—"
        val = f"R$ {d.estimated_value:,.2f}" if d.estimated_value else "R$ 0,00"
        st = d.get_status_display()[:15]

        table_data.append([
            Paragraph(str(idx), style_td_center),
            Paragraph(f"<b>{cod_plac}</b>", style_td_center),
            Paragraph(f"<b>{proc_siga}</b>", style_td_center),
            Paragraph(area[:20], style_td),
            Paragraph(desc, style_td),
            Paragraph(mod[:14], style_td_center),
            Paragraph(sla, style_td_center),
            Paragraph(data_p, style_td_center),
            Paragraph(val, style_td_center),
            Paragraph(st, style_td_center),
        ])

    col_widths = [25, 100, 100, 95, 200, 75, 40, 55, 75, 70]
    t_demandas = Table(table_data, colWidths=col_widths, repeatRows=1)
    t_demandas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')])
    ]))
    elements.append(t_demandas)
    elements.append(Spacer(1, 20))

    # Bloco de Assinaturas e Deliberação
    sign_data = [
        [
            Paragraph("________________________________________<br/><b>Gerência de Compras e Contratos — GCC</b><br/>Consolidação Técnica e Prazos Regimentais", style_td_center),
            Paragraph("________________________________________<br/><b>Diretoria de Administração e Finanças — DAFRI</b><br/>Parecer de Viabilidade Orçamentária", style_td_center),
            Paragraph("________________________________________<br/><b>Diretoria Executiva — REDIR</b><br/>Homologação Colegiada / Ata de Deliberação", style_td_center)
        ]
    ]
    t_sign = Table(sign_data, colWidths=[240, 250, 250])
    t_sign.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(t_sign)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
