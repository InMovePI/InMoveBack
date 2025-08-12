from rest_framework.viewsets import ModelViewSet
from core.models import Dieta
from core.serializers import DietaSerializer

class DietaViewSet(ModelViewSet):
    queryset = Dieta.objects.all()
    serializer_class = DietaSerializer