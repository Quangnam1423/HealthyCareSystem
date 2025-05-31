from rest_framework import serializers
from .models import ChatSession, ChatMessage, HealthSymptom, ChatbotKnowledge

class ChatMessageSerializer(serializers.ModelSerializer):
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'message_type_display', 'content', 'metadata', 'created_at']

class ChatSessionSerializer(serializers.ModelSerializer):
    messages = ChatMessageSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'user', 'session_id', 'title', 'is_active', 'created_at', 'updated_at', 'messages']
        read_only_fields = ['session_id']

class HealthSymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthSymptom
        fields = ['id', 'name', 'description', 'severity_level', 'related_conditions', 'advice']
