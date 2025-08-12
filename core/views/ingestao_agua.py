from rest_framework.viewsets import ModelViewSet

from core.models import IngestaoAgua
from core.serializers import IngestaoAguaSerializer

class IngestaoAguaViewSet(ModelViewSet):
    queryset = IngestaoAgua.objects.all()
    serializer_class = IngestaoAguaSerializer