from rest_framework import viewsets, permissions
from .models import ChatSession, ChatMessage, HealthSymptom, ChatbotKnowledge
from .serializers import ChatSessionSerializer, ChatMessageSerializer, HealthSymptomSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import uuid
from .services import ChatbotService

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

class ChatbotMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated] # Or AllowAny if you want to allow anonymous chat

    def post(self, request, *args, **kwargs):
        user_message_text = request.data.get('message')
        session_id_from_request = request.data.get('session_id') # Renamed to avoid conflict
        user = request.user

        if not user_message_text:
            return Response({'success': False, 'error': 'Message cannot be empty.'}, status=status.HTTP_400_BAD_REQUEST)

        chat_session = None
        new_session_created = False

        if session_id_from_request:
            try:
                # If user is authenticated, ensure session belongs to them
                if user.is_authenticated:
                    chat_session = ChatSession.objects.get(session_id=session_id_from_request, user=user)
                else: # If anonymous is allowed and session_id is provided
                    chat_session = ChatSession.objects.get(session_id=session_id_from_request)
            except ChatSession.DoesNotExist:
                # If session_id is provided but not found or doesn't match user,
                # decide whether to create a new one or error.
                # For now, let's assume if a session_id is given, it should exist.
                # Or, if anonymous, create if not found.
                if not user.is_authenticated: # Allow creating for anonymous if session_id not found
                    chat_session = ChatSession.objects.create(session_id=session_id_from_request) # No user for anonymous
                    new_session_created = True
                else: # Authenticated user provided a non-existent/mismatched session_id
                    # Option 1: Error out
                    # return Response({'success': False, 'error': 'Invalid session ID.'}, status=status.HTTP_400_BAD_REQUEST)
                    # Option 2: Create a new session for this user, ignoring the provided session_id
                    # This might be better to avoid user confusion if they tamper with session_id
                    chat_session = ChatSession.objects.create(user=user, session_id=str(uuid.uuid4()))
                    new_session_created = True
        
        elif user.is_authenticated:
            # No session_id from request, user is authenticated: find or create
            chat_session = ChatSession.objects.filter(user=user, is_active=True).order_by('-updated_at').first()
            if not chat_session:
                chat_session = ChatSession.objects.create(user=user, session_id=str(uuid.uuid4()))
                new_session_created = True
        else:
            # No session_id and anonymous user (if AllowAny)
            # Create a new session for anonymous user
            chat_session = ChatSession.objects.create(session_id=str(uuid.uuid4())) # No user
            new_session_created = True
        
        if not chat_session: # Should not happen if logic above is correct
             return Response({'success': False, 'error': 'Could not establish chat session.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Update session_id to be returned, especially if a new one was generated
        current_session_id = chat_session.session_id

        # Save user message
        user_chat_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='user',
            content=user_message_text,
        )
        # Ensure serializer context includes request if needed by any field (e.g. HyperlinkedRelatedField)
        serializer_context = {'request': request}
        user_message_data = ChatMessageSerializer(user_chat_message, context=serializer_context).data

        # Get bot response
        chatbot_service = ChatbotService()
        bot_response_text = chatbot_service.get_response(user_message_text, user=user if user.is_authenticated else None)

        if bot_response_text is None:
            bot_response_text = "Xin lỗi, tôi không thể xử lý yêu cầu của bạn ngay lúc này."

        # Save bot message
        bot_chat_message = ChatMessage.objects.create(
            session=chat_session,
            message_type='bot',
            content=bot_response_text,
        )
        bot_message_data = ChatMessageSerializer(bot_chat_message, context=serializer_context).data
        
        chat_session.updated_at = timezone.now()
        if not chat_session.title or chat_session.title == "Cuộc trò chuyện mới": # Set title from first user message
            chat_session.title = user_message_text[:60] # Truncate if too long
        chat_session.save()

        return Response({
            'success': True,
            'user_message': user_message_data,
            'bot_message': bot_message_data,
            'session_id': current_session_id 
        }, status=status.HTTP_200_OK)
