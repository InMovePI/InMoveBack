from rest_framework.viewsets import ModelViewSet

from core.models import Treino
from core.serializers import TreinoSerializer

class TreinoViewSet(ModelViewSet):
    queryset = Treino.objects.all()
    serializer_class = TreinoSerializer