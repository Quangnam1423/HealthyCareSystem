from django.db import models
from django.conf import settings

class ChatSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=200, default="Cuộc trò chuyện mới")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    class Meta:
        verbose_name = "Phiên chat"
        verbose_name_plural = "Phiên chat"
        ordering = ['-updated_at']

class ChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('user', 'Người dùng'),
        ('bot', 'Chatbot'),
        ('system', 'Hệ thống'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES)
    content = models.TextField()
    metadata = models.JSONField(blank=True, null=True, help_text="Dữ liệu bổ sung")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_message_type_display()}: {self.content[:50]}..."
    
    class Meta:
        verbose_name = "Tin nhắn chat"
        verbose_name_plural = "Tin nhắn chat"
        ordering = ['created_at']

class HealthSymptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    severity_level = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=1)
    related_conditions = models.TextField(blank=True, null=True)
    advice = models.TextField(help_text="Lời khuyên cho triệu chứng này")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Triệu chứng sức khỏe"
        verbose_name_plural = "Triệu chứng sức khỏe"

class ChatbotKnowledge(models.Model):
    CATEGORY_CHOICES = [
        ('general', 'Tổng quát'),
        ('symptoms', 'Triệu chứng'),
        ('treatments', 'Điều trị'),
        ('prevention', 'Phòng ngừa'),
        ('emergency', 'Cấp cứu'),
        ('medications', 'Thuốc'),
        ('lifestyle', 'Lối sống'),
    ]
    
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    question = models.TextField(help_text="Câu hỏi hoặc từ khóa")
    answer = models.TextField(help_text="Câu trả lời")
    keywords = models.TextField(help_text="Từ khóa liên quan (phân cách bằng dấu phẩy)")
    confidence_score = models.FloatField(default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_category_display()}: {self.question[:50]}..."
    
    class Meta:
        verbose_name = "Kiến thức chatbot"
        verbose_name_plural = "Kiến thức chatbot"
