from rest_framework import serializers
from core.models.chat import ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at', 'session']
        read_only_fields = ['id', 'created_at']
