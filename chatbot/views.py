from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
import uuid
from .models import ChatSession, ChatMessage
from .services import ChatbotService

@login_required
def chat_home(request):
    """Trang chính chatbot"""
    # Tạo session mới hoặc lấy session gần nhất
    session_id = str(uuid.uuid4())
    return redirect('chatbot:session', session_id=session_id)

@login_required
def chat_session(request, session_id):
    """Phiên chat với session_id cụ thể"""
    try:
        # Ensure session_id is a valid UUID before querying
        valid_session_id = uuid.UUID(session_id)
        session = ChatSession.objects.get(session_id=valid_session_id, user=request.user)
    except (ChatSession.DoesNotExist, ValueError):
        # If session_id is invalid or not found, create a new one
        # This handles cases where a user might land here with a bad UUID
        # or if we decide to allow chat_session to initiate new sessions too.
        new_session_uuid = uuid.uuid4()
        session = ChatSession.objects.create(
            user=request.user,
            session_id=new_session_uuid,
            title="Cuộc trò chuyện mới"
        )
        # Redirect to the new session URL to keep the URL consistent with the session_id
        # However, for the initial load, we can proceed with rendering this new session.
        # For simplicity, we will use the new_session_uuid for the current context.
        session_id = str(new_session_uuid) # Update session_id for the context
    
    messages_list = ChatMessage.objects.filter(session=session).order_by('created_at')
    
    # Get recent sessions for sidebar
    recent_sessions = ChatSession.objects.filter(user=request.user).order_by('-updated_at')[:10]
    
    context = {
        'session': session,
        'current_session': session,  # Add alias for template consistency
        'messages': messages_list,
        'session_id': session_id, # Pass the string representation of the UUID
        'recent_sessions': recent_sessions,  # Add recent sessions for sidebar
    }
    return render(request, 'chatbot/chat_session.html', context)

@login_required
def chat_history(request):
    """Lịch sử chat"""
    from django.core.paginator import Paginator
    
    sessions_list = ChatSession.objects.filter(user=request.user).order_by('-updated_at')
    
    # Pagination
    paginator = Paginator(sessions_list, 12)  # 12 sessions per page
    page_number = request.GET.get('page')
    sessions = paginator.get_page(page_number)
    
    context = {'sessions': sessions}
    return render(request, 'chatbot/chat_history.html', context)

@login_required
@require_http_methods(["POST"])
def update_session_title(request, session_id):
    try:
        data = json.loads(request.body)
        new_title = data.get('title')
        if not new_title:
            return JsonResponse({'error': 'Tiêu đề không được để trống.'}, status=400)

        session_uuid = uuid.UUID(session_id)
        session = get_object_or_404(ChatSession, session_id=session_uuid, user=request.user)
        
        session.title = new_title.strip()
        session.save()
        
        return JsonResponse({'success': True, 'new_title': session.title})
    except ValueError:
        return JsonResponse({'error': 'Định dạng session_id không hợp lệ.'}, status=400)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Phiên chat không tồn tại.'}, status=404)
    except Exception as e:
        # Log the exception
        print(f"Error updating session title: {e}")
        return JsonResponse({'error': 'Không thể cập nhật tiêu đề.'}, status=500)

@csrf_exempt # Keep for now, but ensure frontend sends CSRF token in headers for POST
@require_http_methods(["POST"])
@login_required
def send_message(request):
    """API gửi tin nhắn (AJAX)"""
    try:
        data = json.loads(request.body)
        session_id_str = data.get('session_id')
        message_content = data.get('message')
        
        print(f"Received message for session {session_id_str}: {message_content}") # Added logging
        
        if not session_id_str or not message_content:
            return JsonResponse({'error': 'Thiếu thông tin cần thiết: session_id và message là bắt buộc.'}, status=400)
        
        try:
            session_uuid = uuid.UUID(session_id_str)
        except ValueError:
            return JsonResponse({'error': 'Định dạng session_id không hợp lệ.'}, status=400)

        # Lấy hoặc tạo session
        # Note: If session_id is provided, we expect it to exist or be creatable with that ID.
        # The chat_session view should ideally create the session first if it's a new chat page load.
        session, created = ChatSession.objects.get_or_create(
            session_id=session_uuid,
            user=request.user,
            defaults={'title': message_content[:50] if message_content else "Cuộc trò chuyện mới"}
        )
        if created and not session.title: # Ensure title is set if created and message_content was empty initially
            session.title = "Cuộc trò chuyện mới"
            session.save()
        elif not created and not session.title and message_content: # If session existed but had no title
            session.title = message_content[:50]
            session.save()
        
        # Lưu tin nhắn người dùng
        user_message = ChatMessage.objects.create(
            session=session,
            message_type='user',
            content=message_content
        )
        
        # Tạo phản hồi từ bot
        chatbot_service = ChatbotService()
        bot_response_content = chatbot_service.get_response(message_content, request.user)
        
        # Lưu tin nhắn bot
        bot_message = ChatMessage.objects.create(
            session=session,
            message_type='bot',
            content=bot_response_content
        )
        
        session.save() # To update `updated_at`
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.session_id), # Send back the session_id
            'user_message': {
                'id': user_message.id,
                'sender': request.user.get_full_name() or request.user.username,
                'type': 'user',
                'message': user_message.content,
                'timestamp': user_message.created_at.isoformat(),
            },
            'bot_message': {
                'id': bot_message.id,
                'sender': 'HealthyBot',
                'type': 'bot',
                'message': bot_message.content,
                'timestamp': bot_message.created_at.isoformat(),
            }
        })
        
    except Exception as e:
        # Log the exception for server-side debugging
        print(f"Error in send_message: {e}") # Or use proper logging
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@require_http_methods(["POST"])
def delete_session(request, session_id):
    """Xóa session chat"""
    try:
        session_uuid = uuid.UUID(session_id)
        session = get_object_or_404(ChatSession, session_id=session_uuid, user=request.user)
        
        session.delete()
        
        return JsonResponse({'success': True})
    except ValueError:
        return JsonResponse({'error': 'Định dạng session_id không hợp lệ.'}, status=400)
    except Exception as e:
        print(f"Error deleting session: {e}")
        return JsonResponse({'error': 'Không thể xóa cuộc trò chuyện.'}, status=500)
