from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from core.models import Dieta

class DietaSerializer(ModelSerializer):
    usuario_detalhes = serializers.SerializerMethodField()

    class Meta:
        model = Dieta
        fields = ['id', 'objetivo', 'descricao', 'data_inicio', 'usuario', 'usuario_detalhes']

    def get_usuario_detalhes(self, obj):
        # Import local para evitar import circular
        from core.serializers.user import UserSerializer
        return UserSerializer(obj.usuario).data
