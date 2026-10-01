import io
import hashlib
import re
from datetime import datetime, date
from typing import Dict, Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from .services_capacidade import calcular_cronograma_reverso


def normalizar_numero_siga(numero: str) -> str:
    """
    Normaliza a sigla do processo SIGA para o padrão 'TLB-PRO-YYYY/NNNNN'.
    Exemplos aceitos:
    'TLB-PRO-2026-002672' -> 'TLB-PRO-2026/002672'
    'TLB-PRO-2024/03820'  -> 'TLB-PRO-2024/03820'
    '2026/002672'         -> 'TLB-PRO-2026/002672'
    """
    clean = numero.strip().upper()
    if not clean.startswith('TLB-PRO-'):
        clean = 'TLB-PRO-' + clean.replace('TLB-PRO', '').strip('- ')
    
    # Substitui hífen por barra no separador de ano/número se necessário
    # Ex: TLB-PRO-2026-002672 -> TLB-PRO-2026/002672
    m = re.match(r'^TLB-PRO-(\d{4})[-/](\d{4,6})$', clean)
    if m:
        return f"TLB-PRO-{m.group(1)}/{m.group(2)}"
    return clean


def validar_formato_siga(numero: str) -> bool:
    """Verifica se o formato do processo SIGA é plausível (TLB-PRO-YYYY/NNNNN)."""
    norm = normalizar_numero_siga(numero)
    return bool(re.match(r'^TLB-PRO-\d{4}/\d{4,6}$', norm))


def gerar_hash_autenticidade(demand) -> str:
    """Gera um hash SHA-256 a partir dos atributos imutáveis da demanda."""
    raw = (
        f"{demand.id}|{demand.codigo_rastreio_plac}|{demand.description}|"
        f"{demand.estimated_value}|{demand.intended_date}|{demand.created_at}"
    )
    return hashlib.sha256(raw.encode('utf-8')).hexdigest().upper()


def gerar_certidao_pdf(demand) -> bytes:
    """
    Renderiza em memória o PDF oficial da Certidão de Planejamento e Conformidade PLAC
    com base no layout institucional da Telebras e diretrizes da GCC.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    )
    tracking_style = ParagraphStyle(
        'TrackingCode',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a')
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#1e293b')
    )
    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#334155')
    )
    value_style = ParagraphStyle(
        'Value',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#0f172a')
    )
    alert_text = ParagraphStyle(
        'AlertText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#1e293b')
    )
    hash_style = ParagraphStyle(
        'HashStyle',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    )

    story = []

    # 1. Cabeçalho Institucional
    story.append(Paragraph("TELECOMUNICAÇÕES BRASILEIRAS S.A. — TELEBRAS", title_style))
    story.append(Paragraph("DIRETORIA DE ADMINISTRAÇÃO, FINANÇAS E RELAÇÕES COM INVESTIDORES (DAFRI)", subtitle_style))
    story.append(Paragraph("GERÊNCIA DE COMPRAS E CONTRATOS (GCC) — SISTEMA PLAC", subtitle_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=12))

    # 2. Título da Certidão
    story.append(Paragraph("CERTIDÃO DE PLANEJAMENTO E CONFORMIDADE PLAC", title_style))
    story.append(Paragraph("Documento de Vinculação Regimental e Peça nº 01 para Autuação no SIGA", subtitle_style))
    story.append(Spacer(1, 10))

    # 3. Caixa de Destaque do Código de Rastreio
    codigo_rastreio = demand.codigo_rastreio_plac or demand.gerar_codigo_rastreio()
    box_data = [
        [Paragraph(f"CÓDIGO DE RASTREIO DE GESTÃO: <b>{codigo_rastreio}</b>", tracking_style)],
        [Paragraph("<b>ATENÇÃO PROTOCOLO / DEMANDANTE:</b> Esta certidão DEVE constar como peça inicial do processo administrativo no SIGA.", subtitle_style)]
    ]
    box_table = Table(box_data, colWidths=[520])
    box_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1.5, colors.HexColor('#2563eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(box_table)
    story.append(Spacer(1, 12))

    # 4. Dados Básicos da Necessidade (Tabela)
    story.append(Paragraph("1. DADOS DA DEMANDA CADASTRADA", section_title))
    story.append(Spacer(1, 4))

    valor_fmt = "R$ 0,00"
    if demand.estimated_value:
        valor_fmt = f"R$ {demand.estimated_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    modalidade_nome = demand.procurement_type or "Pregão Eletrônico"
    data_pret = demand.intended_date.strftime("%d/%m/%Y") if demand.intended_date else "A definir"

    tabela_dados = [
        [Paragraph("Item / ID PLAC:", label_style), Paragraph(f"#{demand.id}", value_style),
         Paragraph("Diretoria Solicitante:", label_style), Paragraph(str(demand.directorate or 'N/A'), value_style)],
        [Paragraph("Gerência Demandante:", label_style), Paragraph(str(demand.management_unit or 'N/A'), value_style),
         Paragraph("Responsável pelo Registro:", label_style), Paragraph(f"{demand.responsible_name or 'N/A'} ({demand.responsible_email or ''})", value_style)],
        [Paragraph("Natureza da Demanda:", label_style), Paragraph(str(demand.get_nature_type_display() if hasattr(demand, 'get_nature_type_display') else demand.nature_type), value_style),
         Paragraph("Valor Estimado Global:", label_style), Paragraph(f"<b>{valor_fmt}</b>", value_style)],
        [Paragraph("Objeto Resumido:", label_style), Paragraph(str(demand.description or 'N/A'), value_style), "", ""],
        [Paragraph("Justificativa Estratégica:", label_style), Paragraph(str(demand.justification or demand.strategic_alignment or 'Conforme Plano de Negócios.'), value_style), "", ""],
    ]

    t_dados = Table(tabela_dados, colWidths=[110, 150, 110, 150])
    t_dados.setStyle(TableStyle([
        ('SPAN', (1, 3), (3, 3)),
        ('SPAN', (1, 4), (3, 4)),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_dados)
    story.append(Spacer(1, 10))

    # 5. Cronograma Reverso Obrigatório e Prazos Fatais
    story.append(Paragraph("2. CRONOGRAMA REVERSO REGIMENTAL (DIRETRIZ GCC / LEI 13.303)", section_title))
    story.append(Spacer(1, 4))

    crono = calcular_cronograma_reverso(modalidade_nome, demand.intended_date)

    tabela_crono = [
        [Paragraph("Esteira da GCC:", label_style), Paragraph(crono['modalidade_nome'], value_style),
         Paragraph("SLA Regimental GCC:", label_style), Paragraph(f"<b>{crono['sla_regimental_gcc_dias_uteis']} dias úteis</b>", value_style)],
        [Paragraph("Data Pretendida Assinatura:", label_style), Paragraph(f"<b>{data_pret}</b>", value_style),
         Paragraph("Quadrimestre-Alvo:", label_style), Paragraph(f"<b>{crono['quadrimestre_alvo']}</b>", value_style)],
        [Paragraph("Data-Limite Envio à GCC:", label_style), Paragraph(crono['data_limite_envio_gcc'], value_style),
         Paragraph("<b>DATA FATAL ABERTURA SIGA:</b>", label_style), Paragraph(f"<font color='#b91c1c'><b>{crono['data_fatal_abertura_siga']}</b></font>", value_style)],
        [Paragraph("Diagnóstico de Conformidade:", label_style), Paragraph(f"<b>{crono['classificacao_risco']}</b> ({crono['status_viabilidade']})", value_style), "", ""],
    ]

    t_crono = Table(tabela_crono, colWidths=[130, 130, 130, 130])
    t_crono.setStyle(TableStyle([
        ('SPAN', (1, 3), (3, 3)),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (2, 0), (2, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(t_crono)
    story.append(Spacer(1, 10))

    # 6. Instruções Normativas de Autuação e Monitoramento
    story.append(Paragraph("3. INSTRUÇÃO NORMATIVA AO PROTOCOLO E À ÁREA DEMANDANTE", section_title))
    story.append(Spacer(1, 4))

    instrucao_txt = (
        f"<b>1. Autuação no SIGA:</b> O servidor responsável deve abrir o processo no SIGA e registrar "
        f"no campo <i>Assunto/Descrição</i> a menção mandatória: <b>[{codigo_rastreio}] {demand.description[:60]}</b>.<br/>"
        f"<b>2. Vinculação no PLAC:</b> Após receber o número do processo gerado pelo SIGA (ex: <i>TLB-PRO-XXXX/XXXXX</i>), "
        f"o demandante ou diretor deve informar o número no sistema PLAC para acionar o <b>Robô de Gestão Contratual</b>.<br/>"
        f"<b>3. Auditoria Contínua:</b> Todos os despachos, memorandos e notas técnicas ficam sujeitos ao monitoramento "
        f"do Índice de Aderência ao Calendário (IAC) e à Taxa de Execução do Planejamento (TEP)."
    )
    p_inst = Paragraph(instrucao_txt, alert_text)
    t_inst = Table([[p_inst]], colWidths=[520])
    t_inst.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(t_inst)
    story.append(Spacer(1, 14))

    # 7. Assinatura e Carimbo
    story.append(Paragraph("4. VALIDAÇÃO E APROVAÇÃO ESTRATÉGICA", section_title))
    story.append(Spacer(1, 15))

    assinatura_data = [
        [Paragraph("____________________________________________________", ParagraphStyle('Sign', alignment=TA_CENTER, fontName='Helvetica', fontSize=8)),
         Paragraph("____________________________________________________", ParagraphStyle('Sign', alignment=TA_CENTER, fontName='Helvetica', fontSize=8))],
        [Paragraph(f"<b>{demand.responsible_name or 'Responsável pelo Registro'}</b><br/>Área Demandante", ParagraphStyle('SubSign', alignment=TA_CENTER, fontName='Helvetica', fontSize=8)),
         Paragraph(f"<b>Diretor da Área ({demand.directorate or 'Diretoria'})</b><br/>Aprovação e Verificação SIGA", ParagraphStyle('SubSign', alignment=TA_CENTER, fontName='Helvetica', fontSize=8))]
    ]
    t_sign = Table(assinatura_data, colWidths=[260, 260])
    t_sign.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    story.append(t_sign)
    story.append(Spacer(1, 12))

    # 8. Hash de Autenticidade e Rodapé
    hash_code = gerar_hash_autenticidade(demand)
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceAfter=6))
    story.append(Paragraph(f"CHAVE DE AUTENTICIDADE SHA-256: {hash_code}", hash_style))
    story.append(Paragraph(f"Emitido eletronicamente pelo Sistema PLAC-MVP em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}.", ParagraphStyle('Footer', alignment=TA_CENTER, fontName='Helvetica', fontSize=7, textColor=colors.HexColor('#64748b'))))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data


def vincular_processo_siga_demanda(demand_id_ou_codigo, numero_processo_siga: str, usuario=None) -> Dict[str, Any]:
    """
    Amarra o número oficial do processo SIGA (TLB-PRO-XXXX/XXXXX) à demanda correspondente no PLAC.
    Atualiza o campo `siga_process_number` e dispara o gatilho de monitoramento.
    """
    from .models import Demand
    
    clean_siga = normalizar_numero_siga(numero_processo_siga)
    if not validar_formato_siga(clean_siga):
        return {
            "status": "erro",
            "mensagem": f"Formato de processo SIGA inválido: '{numero_processo_siga}'. Padrão esperado: TLB-PRO-YYYY/NNNNN."
        }
        
    # Localiza a demanda por ID numérico ou por Código de Rastreio
    demanda = None
    if isinstance(demand_id_ou_codigo, int) or str(demand_id_ou_codigo).isdigit():
        demanda = Demand.objects.filter(id=int(demand_id_ou_codigo)).first()
    else:
        demanda = Demand.objects.filter(codigo_rastreio_plac=str(demand_id_ou_codigo).strip()).first()
        
    if not demanda:
        return {
            "status": "erro",
            "mensagem": f"Demanda não localizada com identificador '{demand_id_ou_codigo}'."
        }
        
    demanda.siga_process_number = clean_siga
    demanda.save(update_fields=['siga_process_number'])
    
    return {
        "status": "sucesso",
        "mensagem": f"Processo SIGA {clean_siga} vinculado com sucesso à demanda {demanda.codigo_rastreio_plac}!",
        "demand_id": demanda.id,
        "codigo_rastreio_plac": demanda.codigo_rastreio_plac,
        "siga_process_number": demanda.siga_process_number,
        "objeto": demanda.description[:60]
    }
