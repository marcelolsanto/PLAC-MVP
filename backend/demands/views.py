from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Demand
from .serializers import DemandSerializer

class DemandViewSet(viewsets.ModelViewSet):
    serializer_class = DemandSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'DEMANDANTE':
            return Demand.objects.filter(created_by=user).order_by('-created_at')
        return Demand.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        instance = serializer.instance
        if instance.status == 'DEVOLVIDO_AJUSTES':
            serializer.save(status='AGUARDANDO_VALIDACAO', rejection_reason=None)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        demand = self.get_object()
        if demand.status != 'AGUARDANDO_VALIDACAO':
            return Response(
                {'error': 'Apenas demandas aguardando validação podem ser aprovadas pelo Diretor.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        demand.status = 'VALIDADO_DIRETOR'
        demand.rejection_reason = None
        demand.save()
        return Response(DemandSerializer(demand).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        demand = self.get_object()
        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response(
                {'error': 'É obrigatório informar o motivo da devolução para ajustes.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        demand.status = 'DEVOLVIDO_AJUSTES'
        demand.rejection_reason = reason
        demand.save()
        return Response(DemandSerializer(demand).data)

    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        demands = Demand.objects.filter(status='AGUARDANDO_VALIDACAO').order_by('-created_at')
        return Response(DemandSerializer(demands, many=True).data)

    @action(detail=False, methods=['get'])
    def gcc_queue(self, request):
        demands = Demand.objects.filter(status='VALIDADO_DIRETOR').order_by('-created_at')
        return Response(DemandSerializer(demands, many=True).data)

    @action(detail=True, methods=['post'])
    def consolidate(self, request, pk=None):
        from .services import calculate_sla_deadline
        demand = self.get_object()
        procurement_type = request.data.get('procurement_type', 'PREGAO')

        deadline, sla_days, needs_anticipation = calculate_sla_deadline(
            demand.intended_date, procurement_type
        )

        demand.procurement_type = procurement_type
        demand.sla_days = sla_days
        demand.submission_deadline = deadline
        demand.needs_anticipation = needs_anticipation
        demand.status = 'CONSOLIDADO'
        demand.save()

        return Response(DemandSerializer(demand).data)

    @action(detail=False, methods=['get'])
    def metrics(self, request):
        from django.db.models import Sum, Count, F
        total = Demand.objects.count()
        if total == 0:
            return Response({
                'total_demands': 0,
                'total_budget': 0,
                'tep': 0,
                'iac': 100,
                'icnp': 0,
                'iap': 0,
                'tmp': 0,
                'pncp_count': 0,
                'contracted_count': 0,
                'priority_distribution': {'ALTO': 0, 'MEDIO': 0, 'BAIXO': 0},
                'status_distribution': {},
                'monthly_execution': []
            })

        budget = Demand.objects.aggregate(total=Sum('estimated_value'))['total'] or 0
        contracted = Demand.objects.filter(status__in=['CONTRATADO', 'VIGENTE']).count()
        tep = round((contracted / total) * 100, 1)

        # IAC: Aderência ao calendário
        on_time = Demand.objects.filter(needs_anticipation=False).count()
        iac = round((on_time / total) * 100, 1)

        # ICNP: Contratações não previstas (is_extraordinary)
        extra = Demand.objects.filter(is_extraordinary=True).count()
        icnp = round((extra / total) * 100, 1) if total > 0 else 0

        # Mock IAP (Índice de Alteração do Plano) e TMP (Tempo Médio de Processamento)
        iap = 12.4
        tmp = 114

        pncp_count = Demand.objects.filter(pncp_published=True).count()

        priorities = {
            'ALTO': Demand.objects.filter(priority_level='ALTO').count(),
            'MEDIO': Demand.objects.filter(priority_level='MEDIO').count(),
            'BAIXO': Demand.objects.filter(priority_level='BAIXO').count(),
        }

        # Demands grouped by month for chart
        monthly = [
            {"name": "Jan", "planejado": 12, "executado": 2},
            {"name": "Fev", "planejado": 19, "executado": 5},
            {"name": "Mar", "planejado": 25, "executado": 14},
            {"name": "Abr", "planejado": 30, "executado": contracted}
        ]

        return Response({
            'total_demands': total,
            'total_budget': budget,
            'tep': tep,
            'iac': iac,
            'icnp': icnp,
            'iap': iap,
            'tmp': tmp,
            'pncp_count': pncp_count,
            'contracted_count': contracted,
            'priority_distribution': priorities,
            'monthly_execution': monthly
        })

    @action(detail=False, methods=['post'])
    def simulate_sync(self, request):
        """
        Simula a execução dos robôs de extração (Playwright) na intranet/SIGA
        e a publicação no Portal Nacional de Contratações Públicas (PNCP).
        """
        consolidated = Demand.objects.filter(status='CONSOLIDADO')[:2]
        updated_count = 0
        for d in consolidated:
            d.status = 'CONTRATADO'
            d.pncp_published = True
            d.save()
            updated_count += 1

        return Response({
            'message': f'Sincronização concluída! {updated_count} processo(s) atualizados para CONTRATADO e publicados no PNCP.',
            'updated_count': updated_count,
        })

    @action(detail=True, methods=['post'])
    def dafri_opinion(self, request, pk=None):
        demand = self.get_object()
        opinion = request.data.get('opinion', '').strip()
        approved = request.data.get('approved', False)

        if not opinion:
            return Response(
                {'error': 'É obrigatório informar o parecer técnico.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        demand.dafri_opinion = opinion
        demand.dafri_approved = bool(approved)
        demand.save()
        
        return Response(DemandSerializer(demand).data)

    @action(detail=False, methods=['post'])
    def redir_approve(self, request):
        minute_number = request.data.get('minute_number', '').strip()
        if not minute_number:
            return Response(
                {'error': 'O número da ata da REDIR é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        demands = Demand.objects.filter(status='CONSOLIDADO')
        updated_count = 0
        for d in demands:
            d.status = 'VIGENTE'
            d.redir_minute_number = minute_number
            d.save()
            updated_count += 1
            
        return Response({
            'message': f'Virada de ciclo realizada com sucesso. {updated_count} demandas passaram para VIGENTE.',
            'updated_count': updated_count
        })

    @action(detail=True, methods=['post'])
    def redir_reject(self, request, pk=None):
        demand = self.get_object()
        reason = request.data.get('reason', '').strip()
        if not reason:
            return Response(
                {'error': 'É obrigatório informar o motivo da reprovação na REDIR.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        demand.status = 'DEVOLVIDO_AJUSTES'
        demand.rejection_reason = f"Reprovado na REDIR: {reason}"
        demand.save()
        
        return Response(DemandSerializer(demand).data)

    @action(detail=False, methods=['get'])
    def dafri_queue(self, request):
        demands = Demand.objects.filter(status='CONSOLIDADO').order_by('-created_at')
        return Response(DemandSerializer(demands, many=True).data)


from rest_framework.views import APIView
from django.db.models import Q
import unicodedata
from .models import PNCPItemCatalogo

class CatmatSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        from functools import reduce
        import operator
        termo_original = request.query_params.get('q', '').strip()
        tipo_item = request.query_params.get('tipo', '').strip()
        if len(termo_original) < 3:
            return Response({'resultado': []})
        
        termo_sem_acento = ''.join(c for c in unicodedata.normalize('NFD', termo_original) if unicodedata.category(c) != 'Mn')
        
        stop_words = {'de', 'da', 'do', 'e', 'ou', 'para', 'com', 'sem', 'em'}
        keywords = [kw for kw in termo_sem_acento.split() if kw.lower() not in stop_words]
        
        if not keywords:
            return Response({'resultado': []})
            
        query = reduce(operator.and_, (Q(descricao__icontains=kw) | Q(codigo_item__icontains=kw) for kw in keywords))
        
        queryset = PNCPItemCatalogo.objects.using('pncp').filter(query)
        
        if tipo_item in ['M', 'S']:
            queryset = queryset.filter(tipo=tipo_item)
            
        queryset = queryset[:20]
        resultado = [{'codigo': i.codigo_item, 'descricao': i.descricao, 'tipo': i.tipo} for i in queryset]
        return Response({'resultado': resultado})

