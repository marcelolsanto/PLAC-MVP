from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DemandViewSet, CatmatSearchView

router = DefaultRouter()
router.register(r'demands', DemandViewSet, basename='demand')

urlpatterns = [
    path('catmat-search/', CatmatSearchView.as_view(), name='catmat-search'),
    path('', include(router.urls)),
]
