from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from core.views import UserViewSet
from core.views.dieta import DietaViewSet
from core.views.exercicio import ExercicioViewSet
from core.views.ingestao_agua import IngestaoAguaViewSet
from core.views.refeicao import RefeicaoViewSet
from core.views.relatorio_progresso import RelatorioProgressoViewSet

router = DefaultRouter()

router.register(r'dietas', DietaViewSet, basename='dietas')
router.register(r'exercicios', ExercicioViewSet, basename='exercicios')
router.register(r'ingesta-agua', IngestaoAguaViewSet, basename='ingesta-agua')
router.register(r'refeicoes', RefeicaoViewSet, basename='refeicoes')
router.register(r'relatorios', RelatorioProgressoViewSet, basename='relatorios')
router.register(r'usuarios', UserViewSet, basename='usuarios')

urlpatterns = [
    path('admin/', admin.site.urls),
    # OpenAPI 3
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/swagger/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
    # API
    path('api/', include(router.urls)),
]
