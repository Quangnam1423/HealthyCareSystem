import re
import os
from django.conf import settings
from .models import ChatbotKnowledge, HealthSymptom

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

class ChatbotService:
    def __init__(self):
        self.openai_client = None
        if OpenAI and hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            try:
                self.openai_client = OpenAI(
                    api_key=settings.OPENAI_API_KEY,
                    proxies=None,  # Explicitly set proxies to None
                    http_client=None # Explicitly set http_client to avoid proxy issues
                )
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.openai_client = None # Ensure client is None if initialization fails

    def get_response(self, message, user=None):
        """
        Xử lý tin nhắn từ người dùng và trả về phản hồi
        """
        message = message.lower().strip()
        
        # Kiểm tra các câu hỏi thường gặp
        faq_response = self._check_faq(message)
        if faq_response:
            return faq_response
        
        # Kiểm tra triệu chứng
        symptom_response = self._check_symptoms(message)
        if symptom_response:
            return symptom_response
        
        # S? d?ng OpenAI n?u c� API key
        if self.openai_client:
            try:
                return self._get_openai_response(message, user)
            except Exception as e:
                print(f"OpenAI Error: {e}")
        
        # Ph?n h?i m?c d?nh
        return self._get_default_response(message)

    def _check_faq(self, message):
        """
        Kiểm tra kiến thức có sẵn trong database
        """
        try:
            knowledge_items = ChatbotKnowledge.objects.filter(is_active=True)
            
            for item in knowledge_items:
                keywords = [kw.strip() for kw in item.keywords.split(',')]
                if any(keyword.lower() in message for keyword in keywords):
                    return item.answer
                    
            return None
        except Exception:
            return None

    def _check_symptoms(self, message):
        """
        Kiểm tra triệu chứng và đưa ra lời khuyên
        """
        try:
            symptoms = HealthSymptom.objects.all()
            
            for symptom in symptoms:
                if symptom.name.lower() in message:
                    response = f"Về triệu chứng '{symptom.name}':\n\n"
                    response += f"{symptom.description}\n\n"
                    response += f"Lời khuyên: {symptom.advice}\n\n"
                    
                    if symptom.severity_level >= 4:
                        response += "Đây là triệu chứng nghiêm trọng. Bạn nên đi khám bác sĩ ngay lập tức."
                    elif symptom.severity_level >= 3:
                        response += "Bạn nên theo dõi triệu chứng và đi khám bác sĩ nếu tình trạng không cải thiện."
                    else:
                        response += "Triệu chứng này thường không nghiêm trọng, nhưng hãy theo dõi sự thay đổi."
                    
                    return response
                    
            return None
        except Exception:
            return None

    def _get_openai_response(self, message, user=None):
        """
        Sử dụng OpenAI để tạo phản hồi
        """
        system_prompt = """
        Bạn là một trợ lý AI chăm sóc sức khỏe tên HealthyBot. 
        Hãy trả lời bằng tiếng Việt một cách thân thiện và hữu ích.
        Luôn nhắc nhở người dùng rằng bạn chỉ cung cấp thông tin tham khảo 
        và họ nên tham khảo ý kiến bác sĩ cho các vấn đề sức khỏe nghiêm trọng.
        Không đưa ra chẩn đoán y tế cụ thể.
        """
        
        try:
            # Thêm thông tin người dùng nếu có
            user_context = ""
            if user and hasattr(user, 'patient'):
                try:
                    patient = user.patient
                    user_context = f"""
                    Thông tin người dùng:
                    - Họ tên: {user.get_full_name()}
                    - Giới tính: {patient.get_gender_display()}
                    - Tuổi: {patient.age}
                    - Nhóm máu: {patient.blood_group if patient.blood_group else "Không có thông tin"}
                    - Các bệnh mãn tính: {patient.chronic_diseases if patient.chronic_diseases else "Không có thông tin"}
                    - Dị ứng: {patient.allergies if patient.allergies else "Không có thông tin"}
                    """
                except:
                    pass
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt + user_context},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return self._get_default_response(message)

    def _get_default_response(self, message):
        """
        Phản hồi mặc định khi không thể xử lý tin nhắn
        """
        greetings = ['xin chào', 'hello', 'hi', 'chào', 'chào bạn']
        thanks = ['cảm ơn', 'thanks', 'thank you', 'cám ơn']
        health_keywords = ['đau', 'bệnh', 'khỏe', 'sức khỏe', 'triệu chứng', 'thuốc']
        appointment_keywords = ['đặt lịch', 'hẹn', 'khám', 'bác sĩ']
        
        if any(greeting in message for greeting in greetings):
            return """
            Xin chào! Tôi là HealthyBot, trợ lý AI chăm sóc sức khỏe của bạn. 
            
            Tôi có thể giúp bạn:
             Tư vấn về các triệu chứng sức khỏe cơ bản
             Thông tin về việc đặt lịch khám
             Lời khuyên về lối sống lành mạnh
             Trả lời các câu hỏi y tế thường gặp
            
            Bạn có thể hỏi tôi bất cứ điều gì về sức khỏe! 
            """
        
        elif any(thank in message for thank in thanks):
            return "Rất vui được giúp đỡ bạn! Nếu có thêm câu hỏi nào khác về sức khỏe, đừng ngần ngại hỏi tôi nhé! "
        
        elif any(keyword in message for keyword in health_keywords):
            return """
            Tôi hiểu bạn đang quan tâm đến vấn đề sức khỏe. 
            
            Hãy mô tả chi tiết hơn về:
             Triệu chứng bạn đang gặp phải
             Thời gian xuất hiện triệu chứng
             Mức độ nghiêm trọng
            
            Tôi sẽ cố gắng đưa ra lời khuyên phù hợp. Tuy nhiên, hãy nhớ rằng đây chỉ là thông tin tham khảo và bạn nên tham khảo ý kiến bác sĩ chuyên khoa khi cần thiết.
            """
        
        elif any(keyword in message for keyword in appointment_keywords):
            return """
            Để đặt lịch khám, bạn có thể:
            
            1. Sử dụng tính năng "Đặt lịch khám" trên website
            2. Gọi điện thoại đến số hotline: 1900-XXX-XXX
            3. Đến trực tiếp tại bệnh viện
            
            Bạn sẽ cần cung cấp:
             Thông tin cá nhân
             Chuyên khoa muốn khám
             Thời gian mong muốn
             Lý do khám bệnh
            
            Bạn có muốn tôi hướng dẫn chi tiết hơn không?
            """
        
        else:
            return """
            Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. 
            
            Tôi có thể giúp bạn về:
             Tư vấn sức khỏe và triệu chứng
             Hướng dẫn đặt lịch khám
             Thông tin về bác sĩ và chuyên khoa
             Lời khuyên về lối sống lành mạnh
            
            Bạn có thể hỏi cụ thể hơn không? 
            """
