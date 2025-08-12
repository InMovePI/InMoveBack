from rest_framework.serializers import ModelSerializer

from core.models import RelatorioProgresso
from .user import UserSerializer


class RelatorioProgressoSerializer(ModelSerializer):
    usuario_dados = UserSerializer(source='usuario', read_only=True)

    class Meta:
        model = RelatorioProgresso
        fields = ['id', 'data', 'peso_kg', 'percentual_gordura', 'percentual_massa_magra', 'usuario', 'usuario_dados']