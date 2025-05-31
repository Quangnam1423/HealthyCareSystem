from django.contrib import admin
from .models import ChatSession, ChatMessage, HealthSymptom, ChatbotKnowledge

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'user__username', 'user__email')
    readonly_fields = ('session_id',)

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'message_type', 'short_content', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('content', 'session__title', 'session__user__username')
    
    def short_content(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Nội dung'

@admin.register(HealthSymptom)
class HealthSymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'severity_level', 'description')
    list_filter = ('severity_level',)
    search_fields = ('name', 'description', 'advice')
    
@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'is_active', 'confidence_score')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('question', 'answer', 'keywords')
    ordering = ('-confidence_score',)
