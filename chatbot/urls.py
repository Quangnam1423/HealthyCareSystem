from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_home, name='home'),
    path('session/<str:session_id>/', views.chat_session, name='session'),
    path('session/<str:session_id>/title/', views.update_session_title, name='update_session_title'),
    path('history/', views.chat_history, name='history'),
    path('api/message/', views.send_message, name='send_message'),
]
