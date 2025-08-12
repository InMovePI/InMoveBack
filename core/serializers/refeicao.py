from rest_framework.serializers import ModelSerializer

from core.models import Refeicao
from .dieta import DietaSerializer

class RefeicaoSerializer(ModelSerializer):
    dieta_detalhes = DietaSerializer(source='dieta', read_only=True)
    
    class Meta:
        model = Refeicao
        fields = ['id', 'nome_refeicao', 'horario', 'descricao', 'dieta', 'dieta_detalhes']