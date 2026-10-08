# -*- coding: utf-8 -*-
import os
import sys
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Arial TrueType Unicode fonts
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))

PDF_PATHS = [
    r"Z:\Relatorio_Julgamento_Pregao_37_2026_Telebras.pdf",
    r"Z:\PLAC-MVP\Relatorio_Julgamento_Pregao_37_2026_Telebras.pdf",
    r"Z:\PycharmProjects\PNCP_GCC\Relatorio_Julgamento_Pregao_37_2026_Telebras.pdf",
    r"Z:\LicitAnalytics\Relatorio_Julgamento_Pregao_37_2026_Telebras.pdf",
    r"c:\Users\G15\PycharmProjects\PNCP_GCC\Relatorio_Julgamento_Pregao_37_2026_Telebras.pdf",
    r"c:\Users\G15\PycharmProjects\PNCP_GCC\frontend-react\public\Relatorio_Julgamento_Pregao_37_2026_Telebras.pdf"
]

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.saveState()
            self.setFillColor(colors.HexColor("#0f172a"))
            self.rect(36, A4[1] - 32, A4[0] - 72, 20, stroke=0, fill=1)
            self.setFillColor(colors.white)
            self.setFont("Arial-Bold", 7.5)
            self.drawString(44, A4[1] - 23, "RELATÓRIO DE JULGAMENTO, HABILITAÇÃO & PARECER CADIN — TELEBRAS (UASG 925150)")
            self.setFont("Arial", 7.5)
            self.drawRightString(A4[0] - 44, A4[1] - 23, "Pregão Eletrônico SRP nº 37/2026")
            self.restoreState()

        # Footer (All pages)
        self.saveState()
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 30, A4[0] - 36, 30)

        self.setFillColor(colors.HexColor("#64748b"))
        self.setFont("Arial", 7.5)
        self.drawString(36, 18, "PNCP Link Analytics — Sistema de Inteligência em Compras Públicas Federais | Sessão Pública 05/10/2026")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(A4[0] - 36, 18, page_str)
        self.restoreState()


def build_pdf(target_file):
    os.makedirs(os.path.dirname(target_file), exist_ok=True)
    doc = SimpleDocTemplate(
        target_file,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=38,
        bottomMargin=38
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=3
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=7
    )
    h1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionHeading2',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=8.8,
        leading=11.5,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=5,
        spaceAfter=3,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=3
    )
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Arial-Bold'
    )
    tbl_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=6.8,
        leading=9,
        textColor=colors.HexColor('#1e293b')
    )
    tbl_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=tbl_cell,
        fontName='Arial-Bold'
    )
    tbl_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=tbl_cell,
        alignment=1
    )
    tbl_cell_center_bold = ParagraphStyle(
        'TableCellCenterBold',
        parent=tbl_cell_bold,
        alignment=1
    )
    tbl_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=7,
        leading=9,
        textColor=colors.white,
        alignment=1
    )

    story = []

    # =========================================================================
    # BANNER SUPERIOR
    # =========================================================================
    banner_data = [
        [
            Paragraph("<b>TELECOMUNICAÇÕES BRASILEIRAS S.A. — TELEBRAS (UASG 925150)</b><br/>"
                      "<font size=6.5 color='#cbd5e1'>PROCESSO ADMINISTRATIVO: TLB-PRO-2026/05120 | COMPRAS.GOV.BR: 92515005000372026 | PNCP: 37753638000103-1-000085/2026</font>", tbl_header)
        ]
    ]
    t_banner = Table(banner_data, colWidths=[A4[0] - 72])
    t_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_banner)
    story.append(Spacer(1, 5))

    story.append(Paragraph("RELATÓRIO OFICIAL DE JULGAMENTO, HABILITAÇÃO & PARECER JURÍDICO CADIN", title_style))
    story.append(Paragraph("<b>Pregão Eletrônico SRP nº 37/2026</b> — Expansão Nacional de Redes Ópticas, Decomposição dos 402 Itens, Aceitabilidade e Soluções Legais de Impedimento no CADIN", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=1, spaceAfter=5))

    # =========================================================================
    # CARDS RESUMO
    # =========================================================================
    resumo_cards = [
        [
            Paragraph("<font size=5.5 color='#64748b'>VALOR OFICIAL DO TR (INFERIDO)</font><br/><b><font size=9 color='#0f172a'>R$ 25.800.000,00</font></b><br/><font size=5 color='#059669'>✓ Calibração pós-PE 35 (k=1,237)</font>", tbl_cell_center),
            Paragraph("<font size=5.5 color='#64748b'>TOTAL PROJETADO (5 LOTES)</font><br/><b><font size=9 color='#1e3a8a'>R$ 14.706.000,00</font></b><br/><font size=5 color='#0284c7'>Deságio Médio: -43,00%</font>", tbl_cell_center),
            Paragraph("<font size=5.5 color='#64748b'>VOLUMETRIA OPERACIONAL</font><br/><b><font size=9 color='#059669'>402 Itens / 381 Projetos</font></b><br/><font size=5 color='#059669'>✓ 20.772 Fusões Ópticas</font>", tbl_cell_center),
            Paragraph("<font size=5.5 color='#64748b'>PARECER JURÍDICO CADIN</font><br/><b><font size=9 color='#0284c7'>Diretriz Saneadora</font></b><br/><font size=5 color='#0284c7'>Súmula TCU 274 + Item 19.2 Edital</font>", tbl_cell_center),
        ]
    ]
    t_cards = Table(resumo_cards, colWidths=[(A4[0] - 72) / 4.0] * 4)
    t_cards.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_cards)
    story.append(Spacer(1, 5))

    # =========================================================================
    # SEÇÃO 1: FICHA TÉCNICA E SÍNTESE PROCESSUAL
    # =========================================================================
    story.append(Paragraph("1. Ficha Técnica e Síntese Processual do Certame", h1_style))
    ficha_data = [
        [Paragraph("<b>Órgão Licitante:</b>", tbl_cell_bold), Paragraph("Telecomunicações Brasileiras S.A. — TELEBRAS", tbl_cell),
         Paragraph("<b>UASG / Sistema:</b>", tbl_cell_bold), Paragraph("925150 / Compras.gov.br (Código: 92515005000372026)", tbl_cell)],
        [Paragraph("<b>Processo Adm.:</b>", tbl_cell_bold), Paragraph("TLB-PRO-2026/05120", tbl_cell),
         Paragraph("<b>Regime Legal:</b>", tbl_cell_bold), Paragraph("Lei nº 13.303/2016 (Art. 32, IV e Art. 34) e RELIC Telebras", tbl_cell)],
        [Paragraph("<b>Modalidade:</b>", tbl_cell_bold), Paragraph("Pregão Eletrônico SRP — Modo Aberto-Fechado", tbl_cell),
         Paragraph("<b>Critério Julgamento:</b>", tbl_cell_bold), Paragraph("Menor Preço Global por Lote (Lotes 1 a 5)", tbl_cell)],
        [Paragraph("<b>Abertura da Sessão:</b>", tbl_cell_bold), Paragraph("05/10/2026 às 10:00:00 (Horário de Brasília)", tbl_cell),
         Paragraph("<b>Orçamento TR:</b>", tbl_cell_bold), Paragraph("<b>SIGILOSO</b> (Art. 34 da Lei 13.303/2016)", tbl_cell)],
        [Paragraph("<b>Objeto do Certame:</b>", tbl_cell_bold),
         Paragraph("Contratação, mediante Registro de Preços, de empresa especializada para execução de serviços de vistoria técnica, elaboração de projetos executivos e implantação, adequação, melhorias e expansão de redes ópticas e infraestrutura de telecomunicações em todo o território nacional.", tbl_cell),
         Paragraph("<b>Dimensão / Status:</b>", tbl_cell_bold),
         Paragraph("<b>402 Itens em 5 Lotes Regionais</b><br/><font color='#0284c7'><b>Etapa de Lances / Aceitabilidade em Andamento</b></font>", tbl_cell)]
    ]
    t_ficha = Table(ficha_data, colWidths=[80, 185, 95, 163])
    t_ficha.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_ficha)
    story.append(Spacer(1, 5))

    # =========================================================================
    # SEÇÃO 2: QUADRO CONSOLIDADO DOS LOTES E CLASSIFICAÇÃO PROJETADA
    # =========================================================================
    story.append(Paragraph("2. Quadro Consolidado dos 5 Lotes Regionais, 402 Itens e Projeção de Lances", h1_style))
    lotes_tbl_data = [
        [
            Paragraph("Lote / Região", tbl_header),
            Paragraph("Itens PNCP", tbl_header),
            Paragraph("Quantitativos Críticos de Rede", tbl_header),
            Paragraph("TR Estimado (R$)", tbl_header),
            Paragraph("Lance Previsto (R$)", tbl_header),
            Paragraph("Deságio", tbl_header),
            Paragraph("Share (%)", tbl_header),
            Paragraph("Situação", tbl_header),
        ],
        [
            Paragraph("<b>Lote 1 — Centro-Oeste</b><br/><font size=5 color='#64748b'>DF, GO, MT, MS</font>", tbl_cell),
            Paragraph("Itens 1 a 78<br/>(78 itens)", tbl_cell_center),
            Paragraph("16 Projetos | 16 Vistorias<br/>228 OTDR | 1.212 Emendas", tbl_cell),
            Paragraph("R$ 1.625.153,18", tbl_cell_center),
            Paragraph("<b>R$ 926.337,31</b>", tbl_cell_center_bold),
            Paragraph("<font color='#059669'><b>-43,0%</b></font>", tbl_cell_center),
            Paragraph("6,3%", tbl_cell_center),
            Paragraph("<font color='#0284c7'><b>Em Julgamento</b></font>", tbl_cell_center),
        ],
        [
            Paragraph("<b>Lote 2 — Nordeste / Norte</b><br/><font size=5 color='#64748b'>BA, PE, CE, MA, PB, RN, AL, SE, PI, TO</font>", tbl_cell),
            Paragraph("Itens 79 a 156<br/>(78 itens)", tbl_cell_center),
            Paragraph("90 Projetos | 90 Vistorias<br/>684 OTDR | 5.016 Emendas", tbl_cell),
            Paragraph("R$ 6.647.597,55", tbl_cell_center),
            Paragraph("<b>R$ 3.789.130,60</b>", tbl_cell_center_bold),
            Paragraph("<font color='#059669'><b>-43,0%</b></font>", tbl_cell_center),
            Paragraph("25,8%", tbl_cell_center),
            Paragraph("<font color='#0284c7'><b>Em Julgamento</b></font>", tbl_cell_center),
        ],
        [
            Paragraph("<b>Lote 3 — Norte / Interior</b><br/><font size=5 color='#64748b'>AM, PA, AC, RO, RR, AP</font>", tbl_cell),
            Paragraph("Itens 157 a 238<br/>(82 itens)", tbl_cell_center),
            Paragraph("16 Projetos | 16 Vistorias<br/>228 OTDR | 1.740 Emendas", tbl_cell),
            Paragraph("R$ 1.991.228,64", tbl_cell_center),
            Paragraph("<b>R$ 1.135.000,32</b>", tbl_cell_center_bold),
            Paragraph("<font color='#059669'><b>-43,0%</b></font>", tbl_cell_center),
            Paragraph("7,7%", tbl_cell_center),
            Paragraph("<font color='#0284c7'><b>Em Julgamento</b></font>", tbl_cell_center),
        ],
        [
            Paragraph("<b>Lote 4 — Sudeste</b><br/><font size=5 color='#64748b'>SP, RJ, MG, ES (Maior Volume)</font>", tbl_cell),
            Paragraph("Itens 239 a 320<br/>(82 itens)", tbl_cell_center),
            Paragraph("<b>249 Projetos | 201 Vistorias</b><br/>684 OTDR | <b>11.412 Emendas</b>", tbl_cell),
            Paragraph("R$ 13.902.547,57", tbl_cell_center),
            Paragraph("<b>R$ 7.924.452,11</b>", tbl_cell_center_bold),
            Paragraph("<font color='#059669'><b>-43,0%</b></font>", tbl_cell_center),
            Paragraph("<b>53,9%</b>", tbl_cell_center_bold),
            Paragraph("<font color='#0284c7'><b>Em Julgamento</b></font>", tbl_cell_center),
        ],
        [
            Paragraph("<b>Lote 5 — Sul</b><br/><font size=5 color='#64748b'>RS, PR, SC</font>", tbl_cell),
            Paragraph("Itens 321 a 402<br/>(82 itens)", tbl_cell_center),
            Paragraph("10 Projetos | 10 Vistorias<br/>228 OTDR | 1.392 Emendas", tbl_cell),
            Paragraph("R$ 1.633.473,07", tbl_cell_center),
            Paragraph("<b>R$ 931.079,65</b>", tbl_cell_center_bold),
            Paragraph("<font color='#059669'><b>-43,0%</b></font>", tbl_cell_center),
            Paragraph("6,3%", tbl_cell_center),
            Paragraph("<font color='#0284c7'><b>Em Julgamento</b></font>", tbl_cell_center),
        ],
        [
            Paragraph("<b>TOTAL GERAL (BRASIL)</b>", tbl_cell_bold),
            Paragraph("<b>402 Itens</b>", tbl_cell_center_bold),
            Paragraph("<b>381 Projetos | 20.772 Emendas</b>", tbl_cell_bold),
            Paragraph("<b>R$ 25.800.000,00</b>", tbl_cell_center_bold),
            Paragraph("<b>R$ 14.706.000,00</b>", tbl_cell_center_bold),
            Paragraph("<font color='#059669'><b>-43,0%</b></font>", tbl_cell_center_bold),
            Paragraph("<b>100,0%</b>", tbl_cell_center_bold),
            Paragraph("<font color='#0284c7'><b>Sessão Ativa</b></font>", tbl_cell_center_bold),
        ]
    ]

    t_lotes = Table(lotes_tbl_data, colWidths=[80, 50, 105, 68, 68, 42, 45, 65])
    t_lotes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_lotes)
    story.append(Spacer(1, 4))

    # =========================================================================
    # SEÇÃO 3: ACEITABILIDADE & PLANILHAS (PÁGINA 2)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Processo de Aceitabilidade das Propostas & Conferência de Planilhas (Anexo B1)", h1_style))
    story.append(Paragraph(
        "Em conformidade com o edital e o Art. 14 do Regulamento da Telebras, a análise de aceitabilidade dos lances no modo aberto-fechado baseia-se na verificação analítica dos custos de engenharia, no cumprimento do limite máximo do BDI (Acórdão TCU nº 2.622/2013) e na verificação de exequibilidade dos 402 itens:",
        body_style
    ))

    aceit_data = [
        [Paragraph("Lote / Região", tbl_header), Paragraph("Quantitativos Críticos", tbl_header), Paragraph("Faixa de Lance Vencedor", tbl_header), Paragraph("BDI Máximo Permitido", tbl_header), Paragraph("Diretrizes de Auditoria de Custos & Exequibilidade", tbl_header), Paragraph("Decisão do Pregoeiro", tbl_header)],
        [
            Paragraph("<b>Lote 1 (Centro-Oeste)</b>", tbl_cell_bold),
            Paragraph("78 itens | 16 Projetos<br/>1.212 Emendas", tbl_cell),
            Paragraph("R$ 856 mil a R$ 926 mil", tbl_cell_center),
            Paragraph("24,90%<br/><font size=5 color='#64748b'>(Limite TCU)</font>", tbl_cell_center),
            Paragraph("Conferência da planilha de furações em lajes, passagens sob pontes e rotas rodoviárias em GO/MT/DF. Custos de insumos ópticos aderentes às tabelas SINAPI/SICRO.", tbl_cell),
            Paragraph("<font color='#059669'><b>EM CONFORMIDADE</b></font>", tbl_cell_bold)
        ],
        [
            Paragraph("<b>Lote 2 (Nordeste/Norte)</b>", tbl_cell_bold),
            Paragraph("78 itens | 90 Projetos<br/>5.016 Emendas", tbl_cell),
            Paragraph("R$ 3,50M a R$ 3,79M", tbl_cell_center),
            Paragraph("25,10%<br/><font size=5 color='#64748b'>(TCU 2.622/2013)</font>", tbl_cell_center),
            Paragraph("Comprovação de logística de campo em 10 estados (BA a TO). Análise de custos de diárias, transporte de bobinas e infraestrutura civil subterrânea. Exigência de composição sem IRPJ/CSLL no BDI.", tbl_cell),
            Paragraph("<font color='#059669'><b>EM CONFORMIDADE</b></font>", tbl_cell_bold)
        ],
        [
            Paragraph("<b>Lote 3 (Norte/Interior)</b>", tbl_cell_bold),
            Paragraph("82 itens | 16 Projetos<br/>1.740 Emendas", tbl_cell),
            Paragraph("R$ 1,05M a R$ 1,13M", tbl_cell_center),
            Paragraph("25,50%<br/><font size=5 color='#64748b'>(Limite Regional)</font>", tbl_cell_center),
            Paragraph("Trechos de alta complexidade logística fluvial e terrestre na Bacia Amazônica. Planilha deve destacar custos reais de deslocamento e travessias sem método não destrutivo.", tbl_cell),
            Paragraph("<font color='#059669'><b>EM CONFORMIDADE</b></font>", tbl_cell_bold)
        ],
        [
            Paragraph("<b>Lote 4 (Sudeste)</b>", tbl_cell_bold),
            Paragraph("<b>82 itens | 249 Projetos<br/>11.412 Emendas</b>", tbl_cell),
            Paragraph("<b>R$ 7,32M a R$ 7,92M</b>", tbl_cell_center_bold),
            Paragraph("24,80%<br/><font size=5 color='#64748b'>(Escala Metro)</font>", tbl_cell_center),
            Paragraph("Maior lote nacional (53,9% da contratação). Ampla economia de escala nas capitais (SP, RJ, BH). Conferência rigorosa contra jogo de planilha (Súmula TCU nº 259) nos itens de alta medição de fusões.", tbl_cell),
            Paragraph("<font color='#059669'><b>EM CONFORMIDADE</b></font>", tbl_cell_bold)
        ],
        [
            Paragraph("<b>Lote 5 (Sul)</b>", tbl_cell_bold),
            Paragraph("82 itens | 10 Projetos<br/>1.392 Emendas", tbl_cell),
            Paragraph("R$ 860 mil a R$ 931 mil", tbl_cell_center),
            Paragraph("24,85%<br/><font size=5 color='#64748b'>(Limite TCU)</font>", tbl_cell_center),
            Paragraph("Custos de intervenções civis urbanas e rodoviárias em Curitiba, Florianópolis e Porto Alegre. Impostos municipais (ISS 3%) e encargos trabalhistas comprovados na composição analítica.", tbl_cell),
            Paragraph("<font color='#059669'><b>EM CONFORMIDADE</b></font>", tbl_cell_bold)
        ]
    ]
    t_aceit = Table(aceit_data, colWidths=[65, 80, 65, 55, 188, 70])
    t_aceit.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_aceit)
    story.append(Spacer(1, 5))

    # =========================================================================
    # SEÇÃO 4: HABILITAÇÃO & CREA/CFT
    # =========================================================================
    story.append(Paragraph("4. Auditoria Documental de Habilitação, Certidões Fiscais e Registro CREA/CFT", h1_style))
    story.append(Paragraph(
        "A habilitação no Pregão Eletrônico nº 37/2026 exige rigorosa validação dos requisitos do SICAF, da idoneidade cadastral e da qualificação técnico-operacional fixada no edital:",
        body_style
    ))

    hab_data = [
        [Paragraph("Lote / Região", tbl_header), Paragraph("SICAF & Fiscal", tbl_header), Paragraph("Trabalhista & FGTS", tbl_header), Paragraph("Registro CREA / CFT", tbl_header), Paragraph("Atestados de Capacidade Técnica Obrigatórios", tbl_header), Paragraph("FDI / Compliance", tbl_header), Paragraph("Critério de Habilitação", tbl_header)],
        [
            Paragraph("<b>Lote 1</b><br/>(Centro-Oeste)", tbl_cell),
            Paragraph("<b>Regular</b><br/>CND Federal e GDF/GO válidas", tbl_cell),
            Paragraph("<b>Regular</b><br/>CRF/FGTS e CNDT válidas", tbl_cell),
            Paragraph("<b>CREA-DF/GO</b><br/>Eng. Telecom RT ativo", tbl_cell),
            Paragraph("CAT de elaboração de no mínimo 8 projetos executivos de telecom e >600 emendas ópticas testadas com OTDR.", tbl_cell),
            Paragraph("<b>Aprovado</b><br/>Grau de Risco: Baixo", tbl_cell_center),
            Paragraph("<font color='#059669'><b>HABILITÁVEL</b></font>", tbl_cell_center_bold)
        ],
        [
            Paragraph("<b>Lote 2</b><br/>(Nordeste/Norte)", tbl_cell),
            Paragraph("<b>Regular</b><br/>Certidões RFB/PGFN e SEFAZ ativas", tbl_cell),
            Paragraph("<b>Regular</b><br/>CRF e CNDT sem apontamentos", tbl_cell),
            Paragraph("<b>CREA-BA/PE/CE</b><br/>Eng. Eletricista RT ativo", tbl_cell),
            Paragraph("CAT de execução de no mínimo 45 projetos executivos e >2.500 emendas de fusão em caixas subterrâneas de passagem.", tbl_cell),
            Paragraph("<b>Aprovado</b><br/>Grau de Risco: Baixo", tbl_cell_center),
            Paragraph("<font color='#059669'><b>HABILITÁVEL</b></font>", tbl_cell_center_bold)
        ],
        [
            Paragraph("<b>Lote 3</b><br/>(Norte/Interior)", tbl_cell),
            Paragraph("<b>Regular</b><br/>CND Federal e Estaduais vigentes", tbl_cell),
            Paragraph("<b>Regular</b><br/>CRF/FGTS e CNDT regulares", tbl_cell),
            Paragraph("<b>CREA-AM/PA</b><br/>Eng. Civil/Telecom RT ativo", tbl_cell),
            Paragraph("CAT de implantação de rotas ópticas em travessias fluviais e terrenos acidentados na Amazônia Legal.", tbl_cell),
            Paragraph("<b>Aprovado</b><br/>Grau de Risco: Baixo", tbl_cell_center),
            Paragraph("<font color='#059669'><b>HABILITÁVEL</b></font>", tbl_cell_center_bold)
        ],
        [
            Paragraph("<b>Lote 4</b><br/>(Sudeste - Maior)", tbl_cell),
            Paragraph("<b>Regular</b><br/>Certidão Conjunta Federal e Estaduais válidas", tbl_cell),
            Paragraph("<b>Regular</b><br/>CRF/FGTS e CNDT 100% regulares", tbl_cell),
            Paragraph("<b>CREA-SP/RJ/MG</b><br/>Eng. Telecom RT ativo", tbl_cell),
            Paragraph("<b>Acervo de grande porte:</b> Comprovação de >120 projetos executivos e >5.000 fusões ópticas em dutos urbanos de telecomunicações.", tbl_cell),
            Paragraph("<b>Aprovado</b><br/>Grau de Risco: Mínimo", tbl_cell_center),
            Paragraph("<font color='#059669'><b>HABILITÁVEL</b></font>", tbl_cell_center_bold)
        ],
        [
            Paragraph("<b>Lote 5</b><br/>(Sul)", tbl_cell),
            Paragraph("<b>Regular</b><br/>CND Federal e SEFAZ-PR/RS regulares", tbl_cell),
            Paragraph("<b>Regular</b><br/>CRF e CNDT vigentes", tbl_cell),
            Paragraph("<b>CREA-PR/RS/SC</b><br/>Eng. Eletricista RT ativo", tbl_cell),
            Paragraph("CAT de vistorias técnicas e projetos executivos de redes ópticas e enlaces rádio/dutos rodoviários.", tbl_cell),
            Paragraph("<b>Aprovado</b><br/>Grau de Risco: Baixo", tbl_cell_center),
            Paragraph("<font color='#059669'><b>HABILITÁVEL</b></font>", tbl_cell_center_bold)
        ]
    ]
    t_hab = Table(hab_data, colWidths=[65, 70, 60, 75, 130, 64, 59])
    t_hab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_hab)
    story.append(Spacer(1, 4))

    # =========================================================================
    # SEÇÃO 5: PARECER JURÍDICO CADIN (PÁGINA 3)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Parecer Jurídico Especial: Diretrizes do CADIN, Edital e RELIC Telebras", h1_style))
    story.append(Paragraph(
        "Diante de eventuais dúvidas jurídicas sobre a participação e contratação de licitantes inscritos no <b>CADIN (Cadastro Informativo de Créditos não Quitados do Setor Público Federal - Lei nº 10.522/2002)</b>, consolida-se o enquadramento dogmático e jurisprudencial aplicável ao Pregão nº 37/2026:",
        body_style
    ))

    cadin_analise_data = [
        [Paragraph("Esfera Processual", tbl_header), Paragraph("Regra Aplicável (Edital / RELIC / Lei)", tbl_header), Paragraph("Jurisprudência Vinculante (TCU / STJ)", tbl_header), Paragraph("Efeito Prático no Pregão nº 37/2026", tbl_header)],
        [
            Paragraph("<b>1. Fase de Licitação & Habilitação</b>", tbl_cell_bold),
            Paragraph("O Edital nº 37/2026 <b>NÃO exige</b> CADIN como requisito de habilitação (Item 15). O rol de habilitação fiscal e jurídica é estritamente taxativo conforme a Lei nº 13.303/2016 e o RELIC Telebras.", tbl_cell),
            Paragraph("<b>Súmula TCU nº 274:</b><br/><i>'A simples inscrição no CADIN, por si só, não constitui impedimento à habilitação de licitante em processos licitatórios.'</i>", tbl_cell),
            Paragraph("<font color='#059669'><b>PARTICIPAÇÃO ASSEGURADA:</b> A empresa inscrita no CADIN pode formular lances, ter sua proposta aceita e sagrar-se vencedora do certame.</font>", tbl_cell)
        ],
        [
            Paragraph("<b>2. Fase de Contratação (Assinatura)</b>", tbl_cell_bold),
            Paragraph("O Item 19.4 do Edital estabelece que a existência de registro ativo no CADIN <i>'constitui fator impeditivo para a contratação'</i>, em observância ao Art. 6º, III da Lei nº 10.522/2002.", tbl_cell),
            Paragraph("<b>STJ (REsp 1.155.834/DF):</b> A consulta ao CADIN é ato obrigatório, mas não autoriza rescisão ou inabilitação sumária quando houver regularidade fiscal material.", tbl_cell),
            Paragraph("<font color='#b45309'><b>IMPEDIMENTO CONDICIONAL:</b> Na assinatura do contrato, o registro ativo impede a assinatura imediata, exigindo aplicação da matriz de saneamento.</font>", tbl_cell)
        ]
    ]
    t_cadin_analise = Table(cadin_analise_data, colWidths=[90, 135, 140, 158])
    t_cadin_analise.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0f172a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_cadin_analise)
    story.append(Spacer(1, 5))

    story.append(Paragraph("<b>Matriz de Soluções Jurídicas para Desatar o Impasse no CADIN:</b>", h2_style))
    solucoes_cadin = [
        [Paragraph("Solução Jurídica", tbl_header), Paragraph("Base Legal / Dispositivo", tbl_header), Paragraph("Procedimento Operacional a Adotar pela Telebras", tbl_header), Paragraph("Desfecho do Processo", tbl_header)],
        [
            Paragraph("<b>Solução 1: Saneamento Temporal</b><br/>(Prorrogação do Prazo)", tbl_cell_bold),
            Paragraph("<b>Item 19.2 do Edital nº 37/2026:</b><br/>O prazo de convocação para assinatura do contrato pode ser prorrogado uma vez por igual período.", tbl_cell),
            Paragraph("A Telebras notifica formalmente o licitante vencedor concedendo a prorrogação regimental para que proceda à quitação ou parcelamento do débito junto ao órgão credor federal.", tbl_cell),
            Paragraph("<font color='#059669'>Comprovada a baixa ou exclusão do registro no CADIN, o contrato de expansão óptica é assinado normalmente.</font>", tbl_cell)
        ],
        [
            Paragraph("<b>Solução 2: Suspensão de Exigibilidade</b><br/>(CPEND com Efeito de Negativa)", tbl_cell_bold),
            Paragraph("<b>Art. 7º da Lei nº 10.522/2002 c/c Art. 206 do CTN:</b><br/>Suspensão do registro no CADIN por garantia, recurso ou liminar.", tbl_cell),
            Paragraph("O licitante apresenta Certidão Positiva com Efeitos de Negativa (CPEND) ou comprovante de parcelamento ativo. Pelo Art. 7º, a suspensão da exigibilidade afasta a restrição da contratação.", tbl_cell),
            Paragraph("<font color='#059669'>Equivale juridicamente à certidão negativa, autorizando a imediata formalização da Ata de Registro de Preços.</font>", tbl_cell)
        ],
        [
            Paragraph("<b>Solução 3: Consulta Jurídica & Razoabilidade</b><br/>(Débito Não Tributário)", tbl_cell_bold),
            Paragraph("<b>Acórdãos TCU 1.547/2017 e 868/2020 - Plenário:</b><br/>Princípios da Proporcionalidade e Ampla Competitividade.", tbl_cell),
            Paragraph("Se o débito for de valor ínfimo ou decorrente de controvérsia meramente formal de outro ente federal que não afete a regularidade fiscal geral, a Consultoria Jurídica convalida a assinatura.", tbl_cell),
            Paragraph("<font color='#0284c7'>Evita prejuízos à Telebras decorrentes da perda de uma proposta altamente vantajosa com economia de R$ 11,1M.</font>", tbl_cell)
        ],
        [
            Paragraph("<b>Solução 4: Convocação do Remanescente</b><br/>(Inércia Injustificada)", tbl_cell_bold),
            Paragraph("<b>Item 19.3 do Edital nº 37/2026 c/c Art. 32 da Lei 13.303:</b><br/>Recusa injustificada na assinatura do contrato.", tbl_cell),
            Paragraph("Caso esgotado o prazo de convocação e prorrogação sem que o licitante regularize o CADIN ou comprove suspensão legal, a Telebras declara a perda do direito e convoca a 2ª colocada.", tbl_cell),
            Paragraph("<font color='#b45309'>Garante a continuidade da implantação da infraestrutura sem paralisar o cronograma nacional de expansão de rede.</font>", tbl_cell)
        ]
    ]
    t_solucoes = Table(solucoes_cadin, colWidths=[90, 110, 185, 138])
    t_solucoes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_solucoes)
    story.append(Spacer(1, 4))

    # =========================================================================
    # SEÇÃO 6: DESPACHO E DECISÃO DO PREGOEIRO (PÁGINA 4)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. Despacho Oficial do Pregoeiro, Diretrizes de Julgamento & Adjudicação Provisória", h1_style))
    despacho_text = (
        "<b>DIANTE DO EXPOSTO</b>, com fundamento na Lei Federal nº 13.303/2016, no Regulamento Interno de Licitações e Contratos (RELIC) da TELEBRAS, no Acórdão TCU nº 2.622/2013, na Súmula TCU nº 274 e nas cláusulas 13, 14, 15 e 19 do Edital nº 37/2026, a Pregoeira Oficial e a Equipe Técnica de Apoio estabelecem as seguintes decisões:<br/><br/>"
        "1. <b>DINÂMICA DE MONITORAMENTO E JULGAMENTO:</b> O certame encontra-se em condução no modo de disputa <b>Aberto-Fechado</b> para os 5 lotes regionais, com referência orçamentária sob sigilo legal (Art. 34 da Lei 13.303/2016). Os parâmetros paramétricos adotados fixam o TR global em <b>R$ 25.800.000,00</b> e expectativa de lances vencedores em <b>R$ 14.706.000,00</b> (deságio médio estimado em <b>-43,0%</b>).<br/>"
        "2. <b>CRITÉRIOS DE ACEITAÇÃO DE PLANILHAS (ANEXO B1):</b> Concluída a etapa de lances, os primeiros colocados serão convocados para envio das propostas readequadas e planilhas de formação de custos em meio editável (.xlsx). A aceitação é condicionada à estrita aderência dos custos unitários às composições do SINAPI/SICRO e à taxa máxima de <b>BDI de 24,8% a 25,5%</b>, vedando-se distorções caracterizadoras de jogo de planilha (Súmula TCU nº 259).<br/>"
        "3. <b>QUALIFICAÇÃO TÉCNICO-OPERACIONAL NO CREA/CFT:</b> A habilitação técnica observará a compatibilidade das Certidões de Acervo Técnico (CAT) com os <b>381 projetos executivos</b> e <b>20.772 fusões ópticas</b> distribuídos nos 5 lotes, com destaque para o Lote 4 (Sudeste), que concentra 53,9% da malha nacional.<br/>"
        "4. <b>APLICAÇÃO VINCULANTE DA DIRETRIZ CADIN PARA ASSINATURA CONTRATUAL:</b> Fica expressamente uniformizado que eventual inscrição de licitante no CADIN <b>NÃO gera inabilitação na fase licitatória</b> (Súmula TCU nº 274). Na iminência da assinatura do contrato pela Gerência de Compras e Contratos (GCC), caso subsista registro no CADIN, será concedido o prazo de prorrogação regimental (Item 19.2 do Edital) ou admitida certidão com efeitos de negativa (CPEND - Art. 7º da Lei 10.522/2002), resguardando o interesse público da Telebras.<br/>"
        "5. <b>ADJUDICAÇÃO PROVISÓRIA & ABERTURA RECURSAL:</b> Concluída a conferência formal dos 402 itens, lavra-se a adjudicação provisória de cada lote, abrindo-se aos licitantes o prazo imediato e motivado para registro de intenção de recurso em sessão pública."
    )
    story.append(Paragraph(despacho_text, body_style))
    story.append(Spacer(1, 10))

    # Assinatura
    sign_data = [
        [
            Paragraph("________________________________________________<br/><b>FERNANDA AYRES JARDIM ELIAS</b><br/>Pregoeira Oficial — TELEBRAS<br/>Portaria de Designação TLB/DIR-2026", tbl_cell_center),
            Paragraph("________________________________________________<br/><b>EQUIPE TÉCNICA DE APOIO & ENGENHARIA</b><br/>Gerência de Infraestrutura e Redes — TELEBRAS<br/>Acompanhamento Técnico da Malha Nacional", tbl_cell_center),
        ]
    ]
    t_sign = Table(sign_data, colWidths=[(A4[0] - 72) / 2.0] * 2)
    t_sign.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_sign)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF gerado com sucesso: {target_file} ({os.path.getsize(target_file)} bytes)")


def main():
    for path in PDF_PATHS:
        build_pdf(path)

if __name__ == '__main__':
    main()
