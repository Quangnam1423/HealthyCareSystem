from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api_views import ChatSessionViewSet, ChatMessageViewSet, HealthSymptomViewSet, ChatbotMessageAPIView

app_name = 'chatbot'

router = DefaultRouter()
router.register(r'sessions', ChatSessionViewSet, basename='chatsession')
router.register(r'messages', ChatMessageViewSet, basename='chatmessage')
router.register(r'symptoms', HealthSymptomViewSet, basename='healthsymptom')

# Define API patterns first
api_patterns = [
    path('message/', ChatbotMessageAPIView.as_view(), name='chatbot_message_api'),
    # Include other specific APIView paths here if they don't fit the router
]
api_patterns += router.urls # Add ViewSet URLs

# Main urlpatterns for the app
urlpatterns = [
    # Non-API paths
    path('', views.chat_home, name='home'),
    path('session/<str:session_id>/', views.chat_session, name='session'),
    path('session/<str:session_id>/title/', views.update_session_title, name='update_session_title'),
    path('session/<str:session_id>/delete/', views.delete_session, name='delete_session'),
    path('history/', views.chat_history, name='history'),
    
    # Include all API patterns under a common prefix, e.g., 'api/' or 'api/chatbot/'
    # If you want them directly under /chatbot/api/ (as per your current single API endpoint)
    # then the ChatbotMessageAPIView path below is fine.
    # If you want /chatbot/api/chatbot/message, then use the include below.

    # path('api/message/', ChatbotMessageAPIView.as_view(), name='chatbot_message_api'), # For /chatbot/api/message/
    
    # To group under /chatbot/api/chatbot/...
    path('api/chatbot/', include(api_patterns)),
]
