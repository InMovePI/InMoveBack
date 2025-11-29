from rest_framework import serializers
from core.models.chat import ChatSession, ChatMessage
from core.serializers.chat import ChatMessageSerializer


class ChatSessionSerializer(serializers.ModelSerializer):
    # include last message preview
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'last_message']

    def get_last_message(self, obj):
        last = obj.messages.order_by('-created_at').first()
        if not last:
            return None
        return {
            'id': last.id,
            'role': last.role,
            'content': last.content,
            'created_at': last.created_at,
        }
