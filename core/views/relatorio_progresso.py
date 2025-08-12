from rest_framework.viewsets import ModelViewSet

from core.models import RelatorioProgresso
from core.serializers import RelatorioProgressoSerializer

class RelatorioProgressoViewSet(ModelViewSet):
    queryset = RelatorioProgresso.objects.all()
    serializer_class = RelatorioProgressoSerializer