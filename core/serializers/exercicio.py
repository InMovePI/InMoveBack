from rest_framework.serializers import ModelSerializer
from core.models import Exercicio, exercicio

class ExercicioSerializer(ModelSerializer):
    class Meta:
        model = Exercicio
        fields = '__all__'