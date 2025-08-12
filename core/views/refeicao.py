from rest_framework.viewsets import ModelViewSet

from core.models import Refeicao
from core.serializers import RefeicaoSerializer

class RefeicaoViewSet(ModelViewSet):
    queryset = Refeicao.objects.all()
    serializer_class = RefeicaoSerializer