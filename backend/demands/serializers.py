from rest_framework import serializers
from .models import Demand

class DemandSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Demand
        fields = [
            'id', 'description', 'item_type', 'catmat_code',
            'estimated_value', 'intended_date', 'strategic_alignment',
            'f1', 'f2', 'f3', 'f4', 'priority_score', 'priority_level',
            'status', 'rejection_reason', 'procurement_type', 'sla_days',
            'submission_deadline', 'needs_anticipation', 'pncp_published',
            'dafri_opinion', 'dafri_approved', 'redir_minute_number', 'is_extraordinary',
            'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'priority_score', 'priority_level', 'status', 'sla_days',
            'submission_deadline', 'needs_anticipation', 'pncp_published', 
            'dafri_opinion', 'dafri_approved', 'redir_minute_number',
            'created_by_name', 'created_at'
        ]

    def validate(self, attrs):
        for f in ['f1', 'f2', 'f3', 'f4']:
            if attrs.get(f) not in [1, 3, 5]:
                raise serializers.ValidationError({f: "O valor da nota deve ser 1, 3 ou 5."})
        return attrs
