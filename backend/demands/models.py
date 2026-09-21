from django.db import models
from django.conf import settings
from .services import calculate_priority

class Demand(models.Model):
    TYPE_CHOICES = (
        ('BEM', 'Bem'),
        ('SERVICO', 'Serviço'),
        ('TI', 'Tecnologia da Informação (TI)'),
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

    description = models.TextField(verbose_name="Descrição do Objeto")
    item_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Tipo")
    catmat_code = models.CharField(max_length=100, verbose_name="Código/Catálogo CATMAT/CATSER")
    estimated_value = models.DecimalField(max_digits=14, decimal_places=2, verbose_name="Estimativa de Valor")
    intended_date = models.DateField(verbose_name="Data Pretendida de Assinatura")
    strategic_alignment = models.CharField(max_length=255, verbose_name="Vinculação ao Planejamento Estratégico")

    # Fatores de priorização (notas 1, 3 ou 5)
    f1 = models.IntegerField(verbose_name="F1 - Criticidade")
    f2 = models.IntegerField(verbose_name="F2 - Urgência")
    f3 = models.IntegerField(verbose_name="F3 - Impacto")
    f4 = models.IntegerField(verbose_name="F4 - Materialidade")

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
