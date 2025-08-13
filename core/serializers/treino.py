from rest_framework.serializers import ModelSerializer

from core.models import Treino
from .treino_exercicio import TreinoExercicioSerializer
from .user import UserSerializer


class TreinoSerializer(ModelSerializer):
    exercicios_detalhes = TreinoExercicioSerializer(source='treinoexercicio_set', many=True, read_only=True)
    usuario_dados = UserSerializer(source='usuario', read_only=True)
    
    class Meta:
        model = Treino
        fields = ['id', 'nome_treino', 'tipo', 'data_treino', 'duracao_minutos', 'descricao', 'usuario', 'usuario_dados', 'exercicios_detalhes']
        read_only_fields = ['created_at', 'updated_at']