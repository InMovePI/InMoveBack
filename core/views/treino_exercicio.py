from rest_framework.viewsets import ModelViewSet

from core.models import TreinoExercicio
from core.serializers import TreinoExercicioSerializer

class TreinoExercicioViewSet(ModelViewSet):
    queryset = TreinoExercicio.objects.all()
    serializer_class = TreinoExercicioSerializer