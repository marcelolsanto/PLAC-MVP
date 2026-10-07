from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DemandViewSet,
    CatmatSearchView,
    TribunalIAInferirView,
    AmparosLegaisView,
    ComprasExtrairPlanilhaView,
    CadastrarCompraView,
    ProcessosSigaVigentesView,
    SigaExecutarVarreduraView,
    SigaDocumentosView,
    SigaSincronizarKanbanView,
    ContratosPncpVigentesView,
    ContratoTramitacaoInferirView,
    FluxoAreasTelebrasResumoView,
    ContratosTempoMedioAreasView,
    ContratoProcessoParadigmaView,
    ContratosKanbanAreasView,
    InferenciaEstatisticaFluxosView,
    PrevisaoProcessoEstatisticaView,
    CatalogoFluxosGccView,
    VerificarCapacidadeGccView,
    CalcularCronogramaReversoView,
    JanelasCabiveisView,
    EmitirCertidaoPdfView,
    VincularProcessoSigaView,
    CertidaoDadosView,
    MinutaConsolidadaPdfView,
    SentinelaKpisView,
    SentinelaRankingAreasView,
    SentinelaVarreduraView,
    PlanejamentoKanbanTelemetriaView,
    IndicadoresMinutaPlacView,
    CalcularPrioridadeMinutaView,
    PrazosAnexoIIIView,
    PNCPPrecosConsultaView
)

router = DefaultRouter()
router.register(r'demands', DemandViewSet, basename='demand')

urlpatterns = [
    # Rotas Oficiais da Minuta da Diretriz do PLAC v2 (Anexo I, II, III e IV)
    path('planejamento/indicadores-minuta/', IndicadoresMinutaPlacView.as_view(), name='planejamento-indicadores-minuta'),
    path('planejamento/calcular-prioridade-minuta/', CalcularPrioridadeMinutaView.as_view(), name='planejamento-calcular-prioridade-minuta'),
    path('planejamento/prazos-anexo-iii/', PrazosAnexoIIIView.as_view(), name='planejamento-prazos-anexo-iii'),
    path('planejamento/pncp-precos/', PNCPPrecosConsultaView.as_view(), name='planejamento-pncp-precos'),

    # Nova Rota: Telemetria da Esteira Kanban de Planejamento (186 Processos no SIGA)
    path('planejamento/kanban-telemetria/', PlanejamentoKanbanTelemetriaView.as_view(), name='planejamento-kanban-telemetria'),
    # Rotas do Robô Sentinela de Planejamento & Telemetria PLAC (Módulo 4)
    path('planejamento/sentinela/kpis/', SentinelaKpisView.as_view(), name='sentinela-kpis'),
    path('planejamento/sentinela/ranking-areas/', SentinelaRankingAreasView.as_view(), name='sentinela-ranking-areas'),
    path('planejamento/sentinela/varredura/', SentinelaVarreduraView.as_view(), name='sentinela-varredura'),
    # Rota da Minuta Consolidada Oficial do PLAC (PDF para a REDIR)
    path('planejamento/minuta-consolidada-pdf/', MinutaConsolidadaPdfView.as_view(), name='planejamento-minuta-consolidada-pdf'),
    # Rotas da Certidão Oficial do PLAC e Vinculação SIGA
    path('planejamento/demandas/<int:demand_id>/emitir-certidao-pdf/', EmitirCertidaoPdfView.as_view(), name='planejamento-emitir-certidao-pdf'),
    path('planejamento/demandas/<int:demand_id>/certidao-dados/', CertidaoDadosView.as_view(), name='planejamento-certidao-dados'),
    path('planejamento/vincular-processo-siga/', VincularProcessoSigaView.as_view(), name='planejamento-vincular-processo-siga'),
    # Rotas do Robô de Gestão de Planejamento (Capacidade da GCC & Cronograma Reverso)
    path('planejamento/verificar-capacidade/', VerificarCapacidadeGccView.as_view(), name='planejamento-verificar-capacidade'),
    path('planejamento/cronograma-reverso/', CalcularCronogramaReversoView.as_view(), name='planejamento-cronograma-reverso'),
    path('planejamento/janelas-cabiveis/', JanelasCabiveisView.as_view(), name='planejamento-janelas-cabiveis'),
    # Catálogo Completo das 10 Esteiras Oficiais da GCC (Planilha FLUXOS DE COMPRAS)
    path('contratos/catalogo-fluxos-gcc/', CatalogoFluxosGccView.as_view(), name='contratos-catalogo-fluxos-gcc'),
    # Rotas de Inferência Estatística & PERT Calibrado
    path('estatisticas/inferencia-fluxos/', InferenciaEstatisticaFluxosView.as_view(), name='estatisticas-inferencia-fluxos'),
    path('estatisticas/previsao/', PrevisaoProcessoEstatisticaView.as_view(), name='estatisticas-previsao'),
    path('catmat-search/', CatmatSearchView.as_view(), name='catmat-search'),
    path('tribunal-ia/inferir/', TribunalIAInferirView.as_view(), name='tribunal-ia-inferir'),
    path('amparos-legais/', AmparosLegaisView.as_view(), name='amparos-legais'),
    path('compras/extrair-planilha/', ComprasExtrairPlanilhaView.as_view(), name='compras-extrair-planilha'),
    path('compras/cadastrar/', CadastrarCompraView.as_view(), name='compras-cadastrar'),
    # Rotas do Robô Sentinela do SIGA
    path('siga/processos-vigentes/', ProcessosSigaVigentesView.as_view(), name='siga-processos-vigentes'),
    path('siga/executar-varredura/', SigaExecutarVarreduraView.as_view(), name='siga-executar-varredura'),
    path('siga/documentos/', SigaDocumentosView.as_view(), name='siga-documentos'),
    path('siga/sincronizar-kanban/', SigaSincronizarKanbanView.as_view(), name='siga-sincronizar-kanban'),
    # Rotas de Contratos Vigentes PNCP & Fluxo Lógico Telebras
    path('contratos/pncp-vigentes/', ContratosPncpVigentesView.as_view(), name='contratos-pncp-vigentes'),
    path('contratos/inferir-tramitacao/', ContratoTramitacaoInferirView.as_view(), name='contratos-inferir-tramitacao-query'),
    path('contratos/<int:contrato_id>/inferir-tramitacao/', ContratoTramitacaoInferirView.as_view(), name='contratos-inferir-tramitacao'),
    path('contratos/fluxo-areas-telebras/', FluxoAreasTelebrasResumoView.as_view(), name='contratos-fluxo-areas-telebras'),
    path('contratos/tempo-medio-areas/', ContratosTempoMedioAreasView.as_view(), name='contratos-tempo-medio-areas'),
    path('contratos/processo-paradigma/', ContratoProcessoParadigmaView.as_view(), name='contratos-processo-paradigma'),
    path('contratos/kanban-areas/', ContratosKanbanAreasView.as_view(), name='contratos-kanban-areas'),
    path('', include(router.urls)),
]

