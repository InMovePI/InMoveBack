from rest_framework.serializers import ModelSerializer
from .user import UserSerializer
from core.models import Dieta


class DietaSerializer(ModelSerializer):
    usuario_detalhes = UserSerializer(source='usuario', read_only=True)
    
    class Meta:
        model = Dieta
        fields = ['id', 'objetivo', 'descricao', 'data_inicio', 'usuario', 'usuario_detalhes']