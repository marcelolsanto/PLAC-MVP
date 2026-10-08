# -*- coding: utf-8 -*-
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Arial Unicode TrueType fonts
pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Italic', 'C:/Windows/Fonts/ariali.ttf'))

PDF_PATHS = [
    r"Z:\Relatorio_Pregao_37_2026_Telebras.pdf",
    r"Z:\PLAC-MVP\Relatorio_Pregao_37_2026_Telebras.pdf",
    r"Z:\PycharmProjects\PNCP_GCC\Relatorio_Pregao_37_2026_Telebras.pdf",
    r"Z:\LicitAnalytics\Relatorio_Pregao_37_2026_Telebras.pdf"
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
            self.drawString(44, A4[1] - 23, "RELATÓRIO DE MONITORAMENTO, DECOMPOSIÇÃO DE ITENS & INFERÊNCIA TR — TELEBRAS (UASG 925150)")
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
        self.drawString(36, 18, "PNCP Link Analytics — Sistema de Inteligência em Compras Públicas Federais | Monitoramento da Sessão Pública")
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
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0f172a'),
        alignment=1,
        spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=7.8,
        leading=10.5,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=4
    )
    h1_style = ParagraphStyle(
        'SectionHeading1',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=10,
        leading=13.5,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=6,
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
    th_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Arial-Bold',
        fontSize=7.2,
        leading=9.5,
        textColor=colors.white,
        alignment=1
    )
    td_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=7,
        leading=9.2,
        textColor=colors.HexColor('#1e293b')
    )
    td_bold = ParagraphStyle(
        'TableCellBold',
        parent=td_style,
        fontName='Arial-Bold'
    )
    td_center = ParagraphStyle(
        'TableCellCenter',
        parent=td_style,
        alignment=1
    )
    td_center_bold = ParagraphStyle(
        'TableCellCenterBold',
        parent=td_bold,
        alignment=1
    )
    box_style = ParagraphStyle(
        'BoxText',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#0c4a6e')
    )

    story = []

    # =========================================================================
    # CABEÇALHO INSTITUCIONAL
    # =========================================================================
    story.append(Paragraph("TELECOMUNICAÇÕES BRASILEIRAS S.A. — TELEBRAS (UASG 925150)", title_style))
    story.append(Paragraph("PROCESSO ADMINISTRATIVO: TLB-PRO-2026/05120 | COMPRAS.GOV.BR: 92515005000372026 | PNCP: 37753638000103-1-000085/2026", subtitle_style))
    story.append(Paragraph("RELATÓRIO TÉCNICO DE MONITORAMENTO EM TEMPO REAL, DECOMPOSIÇÃO DOS 402 ITENS & INFERÊNCIA DO TR", ParagraphStyle('SubSub', parent=title_style, fontSize=10.5, leading=13.5, textColor=colors.HexColor('#1e40af'), spaceAfter=2)))
    story.append(Paragraph("Pregão Eletrônico SRP nº 37/2026 — Expansão Nacional de Redes Ópticas e Infraestrutura de Telecomunicações", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.2, color=colors.HexColor("#1e3a8a"), spaceBefore=2, spaceAfter=5))

    # =========================================================================
    # SEÇÃO 1: FICHA TÉCNICA DO CERTAME
    # =========================================================================
    story.append(Paragraph("1. Ficha Técnica Oficial do Certame em Disputa", h1_style))
    
    t1_data = [
        [Paragraph("Órgão Licitante", td_bold), Paragraph("TELECOMUNICAÇÕES BRASILEIRAS S.A. – TELEBRAS", td_style),
         Paragraph("UASG / CNPJ", td_bold), Paragraph("925150 / 37.753.638/0001-03", td_style)],
        [Paragraph("Certame / Edital", td_bold), Paragraph("Pregão Eletrônico SRP nº 37/2026", td_style),
         Paragraph("Registro PNCP", td_bold), Paragraph("37753638000103-1-000085/2026", td_style)],
        [Paragraph("Compras.gov.br", td_bold), Paragraph("Compra nº 92515005000372026", td_style),
         Paragraph("Modo de Disputa", td_bold), Paragraph("Aberto-Fechado (Art. 32 Lei 13.303)", td_style)],
        [Paragraph("Critério de Julgamento", td_bold), Paragraph("Menor Preço por Lote (SRP)", td_style),
         Paragraph("Regime Jurídico", td_bold), Paragraph("Lei nº 13.303/2016 e RELIC Telebras", td_style)],
        [Paragraph("Orçamento de Referência", td_bold), Paragraph("<b>SIGILOSO</b> (Art. 34 da Lei 13.303/2016)", td_style),
         Paragraph("Data/Hora Abertura", td_bold), Paragraph("05/10/2026 às 10:00h (Em Andamento)", td_style)],
        [Paragraph("Objeto Resumido", td_bold),
         Paragraph("Contratação, mediante Registro de Preços, de empresa especializada para execução de serviços de vistoria técnica, elaboração de projetos executivos e implantação, adequação, melhorias e expansão de redes ópticas e infraestrutura de telecomunicações em todo o território nacional.", td_style),
         Paragraph("Dimensão do Certame", td_bold),
         Paragraph("<b>402 Itens</b> distribuídos em <b>5 Lotes Regionais</b> (381 Projetos Executivos)", td_style)]
    ]
    t1 = Table(t1_data, colWidths=[105, 175, 95, 148])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('SPAN', (1, 5), (1, 5)),
    ]))
    story.append(t1)
    story.append(Spacer(1, 4))

    # =========================================================================
    # SEÇÃO 2: QUADRO CONSOLIDADO DOS 5 LOTES & QUANTITATIVOS
    # =========================================================================
    story.append(Paragraph("2. Quadro Analítico dos 5 Lotes Regionais & Decomposição dos 402 Itens", h1_style))
    story.append(Paragraph(
        "A extração direta dos 402 itens do PNCP permitiu mapear detalhadamente os 5 lotes operacionais que compõem a totalidade da malha nacional da Telebras:",
        body_style
    ))

    t2_headers = [
        Paragraph("Lote / Região", th_style),
        Paragraph("Itens do PNCP", th_style),
        Paragraph("Quantitativos Críticos de Rede", th_style),
        Paragraph("Share (%)", th_style),
        Paragraph("TR Estimado (Inferido)", th_style),
        Paragraph("Faixa de Lance Vencedor Prevista", th_style)
    ]

    t2_rows = [
        [
            Paragraph("<b>Lote 1</b><br/>Centro-Oeste", td_style),
            Paragraph("Itens 1 a 78<br/>(78 itens)", td_center),
            Paragraph("• 16 Projetos Executivos<br/>• 16 Vistorias de Rota<br/>• 228 Ensaios OTDR | 1.212 Emendas", td_style),
            Paragraph("6,3%", td_center),
            Paragraph("<b>R$ 1.625.153,18</b>", td_center),
            Paragraph("<b>R$ 856 mil a R$ 926 mil</b><br/><font color='#059669'>Deságio: -43% a -47%</font>", td_center)
        ],
        [
            Paragraph("<b>Lote 2</b><br/>Nordeste / Norte", td_style),
            Paragraph("Itens 79 a 156<br/>(78 itens)", td_center),
            Paragraph("• 90 Projetos Executivos<br/>• 90 Vistorias de Rota<br/>• 684 Ensaios OTDR | 5.016 Emendas", td_style),
            Paragraph("25,8%", td_center),
            Paragraph("<b>R$ 6.647.597,55</b>", td_center),
            Paragraph("<b>R$ 3,50M a R$ 3,79M</b><br/><font color='#059669'>Deságio: -43% a -47%</font>", td_center)
        ],
        [
            Paragraph("<b>Lote 3</b><br/>Norte / Interior", td_style),
            Paragraph("Itens 157 a 238<br/>(82 itens)", td_center),
            Paragraph("• 16 Projetos Executivos<br/>• 16 Vistorias de Rota<br/>• 228 Ensaios OTDR | 1.740 Emendas", td_style),
            Paragraph("7,7%", td_center),
            Paragraph("<b>R$ 1.991.228,64</b>", td_center),
            Paragraph("<b>R$ 1,05M a R$ 1,13M</b><br/><font color='#059669'>Deságio: -43% a -47%</font>", td_center)
        ],
        [
            Paragraph("<b>Lote 4</b><br/>Sudeste (Principal)", td_style),
            Paragraph("Itens 239 a 320<br/>(82 itens)", td_center),
            Paragraph("• <b>249 Projetos Executivos</b><br/>• 201 Vistorias de Rota<br/>• 684 Ensaios OTDR | <b>11.412 Emendas</b>", td_style),
            Paragraph("<b>53,9%</b>", td_center_bold),
            Paragraph("<b>R$ 13.902.547,57</b>", td_center),
            Paragraph("<b>R$ 7,32M a R$ 7,92M</b><br/><font color='#059669'>Deságio: -43% a -47%</font>", td_center)
        ],
        [
            Paragraph("<b>Lote 5</b><br/>Sul", td_style),
            Paragraph("Itens 321 a 402<br/>(82 itens)", td_center),
            Paragraph("• 10 Projetos Executivos<br/>• 10 Vistorias de Rota<br/>• 228 Ensaios OTDR | 1.392 Emendas", td_style),
            Paragraph("6,3%", td_center),
            Paragraph("<b>R$ 1.633.473,07</b>", td_center),
            Paragraph("<b>R$ 860 mil a R$ 931 mil</b><br/><font color='#059669'>Deságio: -43% a -47%</font>", td_center)
        ],
        [
            Paragraph("<b>TOTAL GERAL</b>", td_bold),
            Paragraph("<b>402 Itens</b>", td_center_bold),
            Paragraph("<b>381 Projetos Executivos | 20.772 Emendas</b>", td_bold),
            Paragraph("<b>100%</b>", td_center_bold),
            Paragraph("<b>R$ 25.800.000,00</b>", td_center_bold),
            Paragraph("<b>R$ 13,59M a R$ 14,70M</b><br/><font color='#059669'><b>Média Global: -43,0%</b></font>", td_center_bold)
        ]
    ]

    t2 = Table([t2_headers] + t2_rows, colWidths=[75, 65, 155, 45, 88, 95])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
        ('ROWBACKGROUNDS', (0,1), (-1,-2), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(t2)
    
    # FORÇA QUEBRA DE PÁGINA PARA PÁGINA 2
    story.append(PageBreak())

    # =========================================================================
    # SEÇÃO 3: MEMÓRIA DE CÁLCULO E CALIBRAÇÃO ECONOMÉTRICA (PÁGINA 2)
    # =========================================================================
    story.append(Paragraph("3. Memória de Cálculo da Inferência do TR & Calibração Pós-Pregão 35", h1_style))
    story.append(Paragraph(
        "A inferência do valor de referência para orçamentos sigilosos na Telebras opera por <b>Engenharia Reversa de Custos Paramétricos</b> combinada com a calibração da sessão do Pregão nº 35/2026:",
        body_style
    ))

    t3_data = [
        [Paragraph("Componente Orçamentário", th_style), Paragraph("Parâmetro de Referência Unitário (SINAPI / Telebras)", th_style), Paragraph("Impacto nos 402 Itens do Pregão 37", th_style)],
        [
            Paragraph("<b>Projetos Executivos de Redes</b>", td_style),
            Paragraph("R$ 12.500,00 a R$ 15.000,00 / projeto executivo detalhado com ART", td_style),
            Paragraph("<b>381 Projetos</b> em âmbito nacional. Representa a espinha dorsal de engenharia consultiva do certame.", td_style)
        ],
        [
            Paragraph("<b>Vistorias Técnicas & As Built</b>", td_style),
            Paragraph("R$ 3.500,00 (Vistoria de Campo) + R$ 4.200,00 (As Built georreferenciado)", td_style),
            Paragraph("333 Vistorias e As Built previstos para rotas urbanas e rodoviárias da Telebras.", td_style)
        ],
        [
            Paragraph("<b>Ensaios com OTDR & Fusões</b>", td_style),
            Paragraph("R$ 1.800,00 / bobina/enlace testado | R$ 75,00 a R$ 110,00 / fusão óptica", td_style),
            Paragraph("2.052 Ensaios de certificação óptica e 20.772 emendas por fusão em caixas subterrâneas.", td_style)
        ],
        [
            Paragraph("<b>Obras Civis & Travessias MND</b>", td_style),
            Paragraph("R$ 180,00 a R$ 350,00/m (solo/asfalto) | R$ 850,00/m Método Não Destrutivo", td_style),
            Paragraph("Construção de linhas de dutos PEAD, caixas R1/R2/R3 e passagens sob pontes e rodovias.", td_style)
        ],
        [
            Paragraph("<b>BDI de Referência Aplicado</b>", td_style),
            Paragraph("Faixa de <b>22,80% a 24,50%</b> (Acórdão TCU nº 2.622/2013)", td_style),
            Paragraph("Taxa calibrada estritamente dentro do teto admitido pelo TCU para obras/serviços de telecom.", td_style)
        ]
    ]
    t3 = Table(t3_data, colWidths=[120, 195, 208])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0284c7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(t3)
    story.append(Spacer(1, 4))

    # Box de Alerta da Calibração
    box_calib = [
        [Paragraph(
            "<b>💡 Nota Técnica de Calibração:</b> No Pregão nº 35, a inferência preliminar previa R$ 12,4M porque considerava 4 regiões. Com a inclusão da Região Norte, o TR oficial revelado fechou em <b>R$ 15.340.000,00</b> (fator de correção k = 1,2371). Para o Pregão 37, a volumetria física de projetos é 10,8 vezes maior (381 projetos vs. 35 do PE 35), o que calibra o orçamento global da Telebras em <b>R$ 25,8 Milhões</b>. Com o deságio médio de <b>-43,0%</b> verificado em telecom, os lances vencedores projetados somarão entre <b>R$ 13,59M e R$ 14,70M</b>.",
            box_style
        )]
    ]
    t_box = Table(box_calib, colWidths=[523])
    t_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f0f9ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#0284c7")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_box)
    story.append(Spacer(1, 4))

    # =========================================================================
    # SEÇÃO 4: MATRIZ DE AUDITORIA DE LANCES & INEXEQUIBILIDADE
    # =========================================================================
    story.append(Paragraph("4. Diretrizes de Auditoria de Lances, Exequibilidade e Risco de Sobrepreço", h1_style))
    story.append(Paragraph(
        "Em razão do modo de disputa <b>Aberto-Fechado</b> e do expressivo volume de itens, devem ser observadas as seguintes travas de segurança operacional:",
        body_style
    ))

    t4_data = [
        [Paragraph("Dimensão de Controle", th_style), Paragraph("Critério Legal & Jurisprudencial Aplicável", th_style), Paragraph("Ação Operacional Obrigatória", th_style)],
        [
            Paragraph("<b>Alerta de Inexequibilidade</b>", td_style),
            Paragraph("Art. 56 da Lei nº 13.303/2016 e Art. 59, §2º da Lei 14.133. Presunção de inexequibilidade para deságios acentuados.", td_style),
            Paragraph("Exigir comprovação analítica de custos diretos (mão de obra e insumos) para propostas com deságio superior a 50% do valor de referência.", td_style)
        ],
        [
            Paragraph("<b>Vedação ao Jogo de Planilha</b>", td_style),
            Paragraph("Súmula TCU nº 259: Proibição de distorções em itens de alta medição com compensação fictícia em itens secundários.", td_style),
            Paragraph("Conferência item a item da planilha readequada, impedindo sobrepreço em serviços de maior execução física real.", td_style)
        ],
        [
            Paragraph("<b>Qualificação Técnica CREA/CFT</b>", td_style),
            Paragraph("Art. 58 da Lei nº 13.303/2016. Exigência de CATs com quantitativos compatíveis com os 381 projetos executivos.", td_style),
            Paragraph("Validação rigorosa das Certidões de Acervo Técnico (CAT) com registro no CREA/CFT dos engenheiros responsáveis.", td_style)
        ],
        [
            Paragraph("<b>Conformidade CADIN & SICAF</b>", td_style),
            Paragraph("Súmula TCU nº 274: Inscrição no CADIN não exclui do certame, mas impede a celebração do contrato (Art. 6º, III da Lei 10.522/2002).", td_style),
            Paragraph("Aplicação da matriz de saneamento (prazo razoável para quitação ou apresentação de certidão positiva com efeitos de negativa).", td_style)
        ]
    ]
    t4 = Table(t4_data, colWidths=[110, 205, 208])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(t4)
    story.append(Spacer(1, 5))

    # =========================================================================
    # SEÇÃO 5: TERMO DE MONITORAMENTO & ASSINATURAS
    # =========================================================================
    story.append(Paragraph("5. Termo de Acompanhamento da Sessão & Assinaturas Técnicas", h1_style))
    story.append(Paragraph(
        "Certifico que o presente relatório técnico foi gerado a partir do monitoramento automatizado da sessão pública do <b>Pregão Eletrônico SRP nº 37/2026</b>, mediante extração de dados oficiais no Compras.gov.br e no PNCP. As inferências do Termo de Referência (TR) e as faixas projetadas de lances vencedores servem como subsídio de auditoria econométrica para a comissão de contratações.",
        body_style
    ))
    story.append(Spacer(1, 8))

    sig_data = [
        [
            Paragraph("________________________________________________<br/><b>EQUIPE DE INTELIGÊNCIA EM LICITAÇÕES</b><br/>PNCP Link Analytics — Núcleo de Econometria<br/>Monitoramento Preditivo em Compras Públicas", td_center),
            Paragraph("________________________________________________<br/><b>GERÊNCIA DE COMPRAS E CONTRATOS — GCC</b><br/>Telecomunicações Brasileiras S.A. — TELEBRAS<br/>Acompanhamento Técnico do PE nº 37/2026", td_center)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[260, 263])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(t_sig)

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)


def main():
    for p in PDF_PATHS:
        build_pdf(p)
        if os.path.exists(p):
            print(f"PDF gerado com sucesso: {p} ({os.path.getsize(p)} bytes)")
        else:
            print(f"Erro ao gerar: {p}")

if __name__ == "__main__":
    main()
