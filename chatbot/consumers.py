import json
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from .models import ChatSession, ChatMessage
from .services import ChatbotService

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Try to get session_id from URL. If not present, it means it's a new chat.
        self.session_id_str = self.scope['url_route']['kwargs'].get('session_id')
        self.user = self.scope["user"]

        if not self.user or isinstance(self.user, AnonymousUser):
            await self.accept() # Accept connection to send error
            await self.send(text_data=json.dumps({
                'error': 'Bạn cần đăng nhập để sử dụng chatbot.',
                'type': 'system_error' # Add a type for client-side handling
            }))
            await self.close(code=4001) # Custom code for authentication required
            return

        if not self.session_id_str:
            # Generate a new session_id for new chats
            self.session_id_str = str(uuid.uuid4())
            self.newly_created_session = True
        else:
            self.newly_created_session = False
            try:
                # Validate if the provided session_id_str is a valid UUID
                uuid.UUID(self.session_id_str)
            except ValueError:
                await self.accept() # Accept connection to send error
                await self.send(text_data=json.dumps({
                    'error': 'Định dạng session ID không hợp lệ.',
                    'type': 'system_error'
                }))
                await self.close(code=4002) # Custom code for invalid session ID format
                return


        self.room_group_name = f'chat_{self.session_id_str}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        if self.newly_created_session:
             await self.send(text_data=json.dumps({
                'type': 'session_info',
                'session_id': self.session_id_str,
                'message': 'Chat session started.'
            }))

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name') and self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        
        if isinstance(self.user, AnonymousUser): # Should have been caught in connect
            await self.send(text_data=json.dumps({
                'error': 'Bạn cần đăng nhập để sử dụng chatbot.',
                'type': 'system_error'
            }))
            return
        
        # Get or create chat session
        chat_session = await self.get_or_create_session(self.session_id_str, self.user, message_content if self.newly_created_session else "")
        
        # Save user message
        await self.save_message_db(chat_session, message_content, 'user')
        
        # Send user message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': self.user.get_full_name() or self.user.username,
                'message_type': 'user',
                'timestamp': timezone.now().isoformat(),
                'session_id': self.session_id_str
            }
        )
        
        # Get bot response
        bot_response_content = await self.get_bot_response_service(message_content, self.user)
        
        # Save bot message
        await self.save_message_db(chat_session, bot_response_content, 'bot')
        
        # Send bot response to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': bot_response_content,
                'sender': 'HealthyBot',
                'message_type': 'bot',
                'timestamp': timezone.now().isoformat(),
                'session_id': self.session_id_str
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'type': event['message_type'],
            'timestamp': event['timestamp'],
            'session_id': event.get('session_id', self.session_id_str)
        }))

    @database_sync_to_async
    def get_or_create_session(self, session_id_str, user, initial_message=""):
        session_uuid = uuid.UUID(session_id_str)
        session, created = ChatSession.objects.get_or_create(
            session_id=session_uuid,
            user=user,
            defaults={'title': initial_message[:50] if initial_message else 'Cuộc trò chuyện mới'}
        )
        if created and initial_message: # Only update title if created and initial_message is provided
            session.title = initial_message[:50]
            session.save()
        elif not created and not session.title and initial_message: # If session existed but had no title
            session.title = initial_message[:50]
            session.save()
        return session

    @database_sync_to_async
    def save_message_db(self, session, content, message_type):
        message = ChatMessage.objects.create(
            session=session,
            message_type=message_type,
            content=content
        )
        session.updated_at = timezone.now()
        session.save()
        return message

    @database_sync_to_async
    def get_bot_response_service(self, message, user):
        chatbot_service = ChatbotService()
        return chatbot_service.get_response(message, user)

# Ensure ChatbotService and models (ChatSession, ChatMessage) are correctly defined
# and migrations have been run.
