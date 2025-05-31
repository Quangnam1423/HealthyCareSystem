from rest_framework import viewsets, permissions
from .models import ChatSession, ChatMessage, HealthSymptom, ChatbotKnowledge
from .serializers import ChatSessionSerializer, ChatMessageSerializer, HealthSymptomSerializer

class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Chat Sessions
    """
    queryset = ChatSession.objects.all()  # Add this line to fix the error
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)

class ChatMessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Chat Messages - Read only
    """
    queryset = ChatMessage.objects.all()  # Add this line to fix the error
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatMessage.objects.filter(session__user=self.request.user)

class HealthSymptomViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Health Symptoms - Read only
    """
    queryset = HealthSymptom.objects.all()
    serializer_class = HealthSymptomSerializer
    permission_classes = [permissions.AllowAny]
