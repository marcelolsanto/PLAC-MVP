from rest_framework import serializers
from .models import Demand

class DemandSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.username')

    # Metadados de Auditoria, Rastreamento e Proveniência (SIGA / PNCP / PLAC)
    fonte_dados = serializers.SerializerMethodField()
    fonte_dados_label = serializers.SerializerMethodField()
    fonte_tipo = serializers.SerializerMethodField()
    numero_processo_siga = serializers.SerializerMethodField()
    volume_siga = serializers.SerializerMethodField()
    numero_contrato = serializers.SerializerMethodField()
    link_pncp = serializers.SerializerMethodField()
    setor_atual = serializers.SerializerMethodField()
    setor_atual_sigla = serializers.SerializerMethodField()
    localizacao_atual = serializers.SerializerMethodField()
    custodiante_atual = serializers.SerializerMethodField()
    dias_no_setor = serializers.SerializerMethodField()
    ultimo_despacho_siga = serializers.SerializerMethodField()
    documentos = serializers.SerializerMethodField()
    volumes_detalhes = serializers.SerializerMethodField()
    historico_tramitacao = serializers.SerializerMethodField()
    proximos_passos = serializers.SerializerMethodField()
    numero_contrato_futuro = serializers.SerializerMethodField()
    link_siga = serializers.SerializerMethodField()
    link_siga_contrato = serializers.SerializerMethodField()
    tempo_com_usuarios = serializers.SerializerMethodField()
    gargalos_operacao_resumo = serializers.SerializerMethodField()
    etapas_fluxo_dispensa = serializers.SerializerMethodField()
    ciclo_vida_contratual = serializers.SerializerMethodField()
    etapas_fluxo_pregao = serializers.SerializerMethodField()

    def _get_rastreamento(self, obj):
        if not hasattr(obj, '_cached_rastreamento'):
            from .services_siga import RoboSigaService
            obj._cached_rastreamento = RoboSigaService.obter_rastreamento_processo(obj.current_contract)
        return obj._cached_rastreamento

    def get_fonte_dados(self, obj):
        return self._get_rastreamento(obj)["fonte_dados"]

    def get_fonte_dados_label(self, obj):
        return self._get_rastreamento(obj)["fonte_dados_label"]

    def get_fonte_tipo(self, obj):
        return self._get_rastreamento(obj)["fonte_tipo"]

    def get_numero_processo_siga(self, obj):
        if getattr(obj, 'siga_process_number', None):
            return obj.siga_process_number
        return self._get_rastreamento(obj)["numero_processo_siga"]

    def get_volume_siga(self, obj):
        return self._get_rastreamento(obj)["volume_siga"]

    def get_numero_contrato(self, obj):
        return self._get_rastreamento(obj)["numero_contrato"]

    def get_link_pncp(self, obj):
        return self._get_rastreamento(obj)["link_pncp"]

    def get_setor_atual(self, obj):
        return self._get_rastreamento(obj)["setor_atual"]

    def get_setor_atual_sigla(self, obj):
        return self._get_rastreamento(obj)["setor_atual_sigla"]

    def get_localizacao_atual(self, obj):
        return self._get_rastreamento(obj)["localizacao_atual"]

    def get_custodiante_atual(self, obj):
        return self._get_rastreamento(obj)["custodiante_atual"]

    def get_dias_no_setor(self, obj):
        return self._get_rastreamento(obj)["dias_no_setor"]

    def get_ultimo_despacho_siga(self, obj):
        return self._get_rastreamento(obj)["ultimo_despacho_siga"]

    def get_documentos(self, obj):
        return self._get_rastreamento(obj).get("documentos", [])

    def get_volumes_detalhes(self, obj):
        return self._get_rastreamento(obj).get("volumes_detalhes", [])

    def get_historico_tramitacao(self, obj):
        return self._get_rastreamento(obj).get("historico_tramitacao", [])

    def get_proximos_passos(self, obj):
        return self._get_rastreamento(obj).get("proximos_passos", [])

    def get_numero_contrato_futuro(self, obj):
        return self._get_rastreamento(obj).get("numero_contrato_futuro")

    def get_link_siga(self, obj):
        return self._get_rastreamento(obj).get("link_siga")

    def get_link_siga_contrato(self, obj):
        return self._get_rastreamento(obj).get("link_siga_contrato")

    def get_tempo_com_usuarios(self, obj):
        return self._get_rastreamento(obj).get("tempo_com_usuarios", [])

    def get_gargalos_operacao_resumo(self, obj):
        return self._get_rastreamento(obj).get("gargalos_operacao_resumo", [])

    def get_etapas_fluxo_dispensa(self, obj):
        return self._get_rastreamento(obj).get("etapas_fluxo_dispensa", [])

    def get_ciclo_vida_contratual(self, obj):
        return self._get_rastreamento(obj).get("ciclo_vida_contratual", {})

    def get_etapas_fluxo_pregao(self, obj):
        return self._get_rastreamento(obj).get("etapas_fluxo_pregao", [])

    class Meta:
        model = Demand
        fields = [
            'id',
            # Bloco 1 — Identificação
            'directorate', 'management_unit', 'responsible_name', 'responsible_email', 'nature_type',
            # Bloco 2 — Objeto
            'description', 'item_type', 'catmat_code', 'quantity', 'unit', 'justification', 'strategic_alignment',
            # Bloco 3 — Vinculações
            'current_contract', 'depends_on_item', 'public_policy', 'is_confidential', 'confidentiality_basis',
            # Bloco 4 — Valores
            'budget_source', 'estimated_value', 'estimated_source',
            # Bloco 5 — Prazos e Priorização
            'intended_date', 'f1', 'f2', 'f3', 'f4', 'score_justification',
            'priority_score', 'priority_level',
            # Status e fluxo
            'status', 'rejection_reason', 'procurement_type', 'sla_days',
            'submission_deadline', 'needs_anticipation', 'pncp_published',
            # Bloco 6 — GCC
            'gcc_notes', 'aggregated_to_item',
            # UC05/UC06/UC07
            # Governança e Rastreabilidade SIGA
            'codigo_rastreio_plac', 'siga_process_number', 'certidao_emitida_em', 'quadrimestre_alvo',
            'created_by_name', 'created_at',
            # Metadados de Rastreamento e Proveniência (SIGA / PNCP / PLAC)
            'fonte_dados', 'fonte_dados_label', 'fonte_tipo',
            'numero_processo_siga', 'volume_siga', 'numero_contrato', 'numero_contrato_futuro', 'link_pncp',
            'link_siga', 'link_siga_contrato',
            'setor_atual', 'setor_atual_sigla', 'localizacao_atual', 'custodiante_atual',
            'dias_no_setor', 'ultimo_despacho_siga',
            'documentos', 'volumes_detalhes', 'historico_tramitacao', 'proximos_passos',
            'tempo_com_usuarios', 'gargalos_operacao_resumo', 'etapas_fluxo_dispensa',
            'ciclo_vida_contratual', 'etapas_fluxo_pregao'
        ]
        read_only_fields = [
            'priority_score', 'priority_level', 'status', 'sla_days',
            'submission_deadline', 'needs_anticipation', 'pncp_published',
            'gcc_notes', 'aggregated_to_item',
            'dafri_opinion', 'dafri_approved', 'redir_minute_number',
            'created_by_name', 'created_at',
            'fonte_dados', 'fonte_dados_label', 'fonte_tipo',
            'numero_processo_siga', 'volume_siga', 'numero_contrato', 'numero_contrato_futuro', 'link_pncp',
            'link_siga', 'link_siga_contrato',
            'setor_atual', 'setor_atual_sigla', 'localizacao_atual', 'custodiante_atual',
            'dias_no_setor', 'ultimo_despacho_siga',
            'documentos', 'volumes_detalhes', 'historico_tramitacao', 'proximos_passos',
            'tempo_com_usuarios', 'gargalos_operacao_resumo', 'etapas_fluxo_dispensa',
            'ciclo_vida_contratual', 'etapas_fluxo_pregao'
        ]

    def validate(self, attrs):
        for f in ['f1', 'f2', 'f3', 'f4']:
            if attrs.get(f) not in [1, 3, 5]:
                raise serializers.ValidationError({f: "O valor da nota deve ser 1, 3 ou 5."})
        return attrs
