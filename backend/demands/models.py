from django.db import models
from django.conf import settings
from .services import calculate_priority

class Demand(models.Model):
    TYPE_CHOICES = (
        ('BEM', 'Bem'),
        ('SERVICO', 'Serviço'),
        ('TI', 'Tecnologia da Informação (TI)'),
    )

    NATURE_CHOICES = (
        ('NOVA', 'Nova contratação'),
        ('PRORROGACAO', 'Prorrogação'),
        ('ADITIVO', 'Aditivo'),
        ('REAJUSTE', 'Reajuste'),
    )

    PRIORITY_LEVEL_CHOICES = (
        ('ALTO', 'Alto'),
        ('MEDIO', 'Médio'),
        ('BAIXO', 'Baixo'),
    )

    STATUS_CHOICES = (
        ('AGUARDANDO_VALIDACAO', 'Aguardando validação superior'),
        ('VALIDADO_DIRETOR', 'Validado pela Diretoria'),
        ('DEVOLVIDO_AJUSTES', 'Devolvido para Ajustes'),
        ('CONSOLIDADO', 'Consolidado pela GCC'),
        ('CONTRATADO', 'Contratado / Publicado no PNCP'),
        ('VIGENTE', 'Vigente'),
    )

    # ── Bloco 1 — Identificação ──
    directorate = models.CharField(max_length=200, blank=True, null=True, verbose_name="Diretoria")
    management_unit = models.CharField(max_length=200, blank=True, null=True, verbose_name="Gerência demandante")
    responsible_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="Responsável pelo registro")
    responsible_email = models.EmailField(blank=True, null=True, verbose_name="E-mail do responsável")
    nature_type = models.CharField(max_length=20, choices=NATURE_CHOICES, default='NOVA', verbose_name="Natureza")

    # ── Bloco 2 — Objeto ──
    description = models.TextField(verbose_name="Descrição do Objeto")
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo do objeto")
    catmat_code = models.CharField(max_length=100, verbose_name="Código/Catálogo CATMAT/CATSER")
    quantity = models.IntegerField(default=1, verbose_name="Quantidade")
    unit = models.CharField(max_length=100, blank=True, null=True, verbose_name="Unidade")
    justification = models.TextField(blank=True, null=True, verbose_name="Justificativa da necessidade")
    strategic_alignment = models.CharField(max_length=255, verbose_name="Objetivo estratégico do PEI")

    # ── Bloco 3 — Vinculações ──
    current_contract = models.CharField(max_length=200, blank=True, null=True, verbose_name="Contrato vigente (nº e processo)")
    depends_on_item = models.CharField(max_length=50, blank=True, null=True, verbose_name="Depende do item nº")
    public_policy = models.CharField(max_length=255, blank=True, null=True, verbose_name="Projeto ou política pública")
    is_confidential = models.BooleanField(default=False, verbose_name="Sujeito a sigilo")
    confidentiality_basis = models.CharField(max_length=255, blank=True, null=True, verbose_name="Fundamento do sigilo")

    # ── Bloco 4 — Valores ──
    budget_source = models.CharField(max_length=100, blank=True, null=True, verbose_name="Fonte orçamentária")
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Valor estimado 2027 (R$)")
    estimated_source = models.CharField(max_length=200, blank=True, null=True, verbose_name="Fonte da estimativa")

    # ── Bloco 5 — Prazos e Priorização ──
    intended_date = models.DateField(verbose_name="Data Pretendida de Assinatura")
    f1 = models.IntegerField(verbose_name="F1 - Criticidade")
    f2 = models.IntegerField(verbose_name="F2 - Descontinuidade")
    f3 = models.IntegerField(verbose_name="F3 - Obrigação Legal")
    f4 = models.IntegerField(verbose_name="F4 - Materialidade")
    score_justification = models.TextField(blank=True, null=True, verbose_name="Justificativa das notas")

    # Resultados calculados
    priority_score = models.IntegerField(blank=True, null=True, verbose_name="Pontuação de Prioridade")
    priority_level = models.CharField(max_length=10, choices=PRIORITY_LEVEL_CHOICES, blank=True, verbose_name="Grau de Prioridade")

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='AGUARDANDO_VALIDACAO', verbose_name="Status")
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Motivo de Devolução")

    # Campos de consolidação da GCC (UC03)
    procurement_type = models.CharField(max_length=30, blank=True, null=True, verbose_name="Forma de Contratação")
    sla_days = models.IntegerField(blank=True, null=True, verbose_name="Prazo de SLA (dias)")
    submission_deadline = models.DateField(blank=True, null=True, verbose_name="Data-limite de Encaminhamento")
    needs_anticipation = models.BooleanField(default=False, verbose_name="Alerta de Antecipação para Ano Anterior")
    pncp_published = models.BooleanField(default=False, verbose_name="Publicado no PNCP")

    # ── Bloco 6 — Uso da GCC ──
    gcc_notes = models.TextField(blank=True, null=True, verbose_name="Observações da GCC")
    aggregated_to_item = models.CharField(max_length=50, blank=True, null=True, verbose_name="Agregado ao item nº")

    # Campos de deliberação executiva (UC05/UC06/UC07)
    dafri_opinion = models.TextField(blank=True, null=True, verbose_name="Parecer Técnico DAFRI")
    dafri_approved = models.BooleanField(default=False, verbose_name="Aprovação DAFRI")
    redir_minute_number = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número da Ata REDIR")
    is_extraordinary = models.BooleanField(default=False, verbose_name="Demanda Extraordinária (Fora do Ciclo)")

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="demands")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Processa a fórmula de cálculo de forma invisível
        score, level = calculate_priority(self.f1, self.f2, self.f3, self.f4)
        self.priority_score = score
        self.priority_level = level
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Demanda #{self.id} - {self.description[:40]} ({self.priority_level})"

class PNCPItemCatalogo(models.Model):
    codigo_item = models.CharField(max_length=20, db_column='codigo_item', primary_key=True)
    descricao = models.CharField(max_length=1000, db_column='descricao')
    tipo = models.CharField(max_length=1, db_column='tipo')
    codigo_pai = models.CharField(max_length=20, null=True, blank=True, db_column='codigo_pai')

    class Meta:
        managed = False
        db_table = 'compras_item_catalogo_local'

