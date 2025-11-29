from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from core.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'data_nascimento', 'genero',
            'altura_cm', 'peso_kg', 'objetivo', 'meta_peso', 'dias_treino', 'grupo_foco'
        ]
        read_only_fields = ['id']

class UserCreateSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'password', 'data_nascimento', 'genero',
            'altura_cm', 'peso_kg', 'objetivo', 'meta_peso', 'dias_treino', 'grupo_foco'
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'data_nascimento': {'required': False, 'allow_null': True},
            'genero': {'required': False, 'allow_null': True},
            'altura_cm': {'required': False, 'allow_null': True},
            'peso_kg': {'required': False, 'allow_null': True},
            'objetivo': {'required': False, 'allow_null': True},
            'meta_peso': {'required': False, 'allow_null': True},
            'dias_treino': {'required': False, 'allow_null': True},
            'grupo_foco': {'required': False, 'allow_null': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)

        # Defaults se não vier do frontend
        validated_data.setdefault('data_nascimento', None)
        validated_data.setdefault('genero', None)
        validated_data.setdefault('altura_cm', None)
        validated_data.setdefault('peso_kg', None)

        user = User.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            **validated_data,
        )
        return user
