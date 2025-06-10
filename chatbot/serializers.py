from rest_framework import serializers
from .models import ChatSession, ChatMessage, HealthSymptom, ChatbotKnowledge

class ChatMessageSerializer(serializers.ModelSerializer):
    message_type_display = serializers.CharField(source='get_message_type_display', read_only=True)
    message = serializers.CharField(source='content', read_only=True)  # Alias content as message
    sender = serializers.CharField(source='message_type', read_only=True)  # Alias message_type as sender
    type = serializers.CharField(source='message_type', read_only=True)  # Alias message_type as type
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)  # Alias created_at as timestamp
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_type', 'message_type_display', 'content', 'metadata', 'created_at', 
                 'message', 'sender', 'type', 'timestamp']

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
