from rest_framework.serializers import ModelSerializer, IntegerField
from core.models import TreinoExercicio
from .exercicio import ExercicioSerializer

class TreinoExercicioSerializer(ModelSerializer):
    exercicio_detalhes = ExercicioSerializer(source='exercicio', read_only=True)
    exercicio_id = IntegerField(write_only=True)

    class Meta:
        model = TreinoExercicio
        fields = ['treino', 'exercicio_id', 'exercicio_detalhes', 'series', 'repeticoes', 'carga_kg']