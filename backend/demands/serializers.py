from rest_framework import serializers
from .models import Demand

class DemandSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.username')

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
            'dafri_opinion', 'dafri_approved', 'redir_minute_number', 'is_extraordinary',
            'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'priority_score', 'priority_level', 'status', 'sla_days',
            'submission_deadline', 'needs_anticipation', 'pncp_published',
            'gcc_notes', 'aggregated_to_item',
            'dafri_opinion', 'dafri_approved', 'redir_minute_number',
            'created_by_name', 'created_at'
        ]

    def validate(self, attrs):
        for f in ['f1', 'f2', 'f3', 'f4']:
            if attrs.get(f) not in [1, 3, 5]:
                raise serializers.ValidationError({f: "O valor da nota deve ser 1, 3 ou 5."})
        return attrs
