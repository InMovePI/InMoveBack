from rest_framework.serializers import ModelSerializer

from core.models import IngestaoAgua
from .user import UserSerializer

class IngestaoAguaSerializer(ModelSerializer):
    usuario_dados = UserSerializer(source='usuario', read_only=True)

    class Meta:
        model = IngestaoAgua
        fields = ['id', 'data', 'quantidade_ml', 'horario', 'usuario', 'usuario_dados']