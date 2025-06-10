from .models import ChatbotKnowledge, HealthSymptom

class ChatbotService:
    def __init__(self):
        pass

    def get_response(self, message, user=None):
        """
        Xử lý tin nhắn từ người dùng và trả về phản hồi dựa trên kiến thức nội bộ.
        """
        message_lower = message.lower().strip()

        # 1. Kiểm tra các câu hỏi thường gặp từ ChatbotKnowledge
        faq_response = self._check_faq(message_lower)
        if faq_response:
            return faq_response

        # 2. Kiểm tra triệu chứng từ HealthSymptom
        symptom_response = self._check_symptoms(message_lower)
        if symptom_response:
            return symptom_response

        # 3. Phản hồi mặc định nếu không tìm thấy gì phù hợp
        return self._get_default_response(message_lower)

    def _check_faq(self, message):
        """
        Kiểm tra kiến thức có sẵn trong database (ChatbotKnowledge).
        """
        try:
            knowledge_items = ChatbotKnowledge.objects.filter(is_active=True)
            
            best_match = None
            highest_keyword_match_count = 0

            for item in knowledge_items:
                keywords = [kw.strip().lower() for kw in item.keywords.split(',') if kw.strip()]
                
                current_match_count = 0
                for keyword in keywords:
                    if keyword in message:
                        current_match_count +=1
                
                if current_match_count > 0 and current_match_count > highest_keyword_match_count:
                    highest_keyword_match_count = current_match_count
                    best_match = item.answer
                elif item.question.lower().strip() in message and not best_match and highest_keyword_match_count == 0: # Nếu không có keyword nào khớp, thử khớp cả câu hỏi
                    best_match = item.answer
            
            return best_match
        except Exception as e:
            print(f"Error in _check_faq: {e}")
            return None

    def _check_symptoms(self, message):
        """
        Kiểm tra triệu chứng và đưa ra lời khuyên từ HealthSymptom.
        """
        try:
            symptoms = HealthSymptom.objects.all()
            
            found_symptoms_responses = []

            for symptom in symptoms:
                if symptom.name.lower() in message:
                    response_parts = [
                        f"Thông tin về triệu chứng '{symptom.name}':",
                        f"- Mô tả: {symptom.description}"
                    ]
                    if symptom.advice:
                         response_parts.append(f"- Lời khuyên: {symptom.advice}")

                    if symptom.severity_level >= 4:
                        response_parts.append("⚠️ Đây có thể là triệu chứng nghiêm trọng. Bạn nên đi khám bác sĩ ngay lập tức.")
                    elif symptom.severity_level >= 3:
                        response_parts.append("⚠️ Bạn nên theo dõi triệu chứng và đi khám bác sĩ nếu tình trạng không cải thiện.")
                    else:
                        response_parts.append("💡 Triệu chứng này có thể không quá nghiêm trọng, nhưng hãy theo dõi sự thay đổi.")
                    
                    found_symptoms_responses.append("\\n".join(response_parts))
            
            if found_symptoms_responses:
                return "\\n\\n".join(found_symptoms_responses)
            return None
        except Exception as e:
            print(f"Error in _check_symptoms: {e}")
            return None

    def _get_default_response(self, message):
        """
        Phản hồi mặc định khi không thể xử lý tin nhắn.
        """
        greetings = ['xin chào', 'hello', 'hi', 'chào', 'chào bạn']
        thanks = ['cảm ơn', 'thanks', 'thank you', 'cám ơn']
        
        if any(greeting in message for greeting in greetings):
            return (
                "Xin chào! Tôi là HealthyBot, trợ lý AI chăm sóc sức khỏe của bạn. 🏥\\n\\n"
                "Tôi có thể giúp bạn:\\n"
                "• Tư vấn về các triệu chứng sức khỏe cơ bản\\n"
                "• Thông tin về việc đặt lịch khám\\n"
                "• Lời khuyên về lối sống lành mạnh\\n"
                "• Trả lời các câu hỏi y tế thường gặp\\n\\n"
                "Bạn có thể hỏi tôi bất cứ điều gì về sức khỏe! 😊"
            )
        
        if any(thank in message for thank in thanks):
            return "Rất vui được giúp đỡ bạn! Nếu có thêm câu hỏi nào khác về sức khỏe, đừng ngần ngại hỏi tôi nhé! 😊"
        
        return (
            "Xin lỗi, tôi chưa hiểu rõ câu hỏi của bạn. \\n\\n"
            "Tôi có thể giúp bạn về:\\n"
            "• Tư vấn sức khỏe và triệu chứng\\n"
            "• Hướng dẫn đặt lịch khám\\n"
            "• Thông tin về bác sĩ và chuyên khoa\\n"
            "• Lời khuyên về lối sống lành mạnh\\n\\n"
            "Bạn có thể mô tả chi tiết hơn hoặc đặt câu hỏi cụ thể hơn được không? 😊"
        )
