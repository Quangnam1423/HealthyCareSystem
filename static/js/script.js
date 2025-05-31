// Main JavaScript for HealthyCareSystem

document.addEventListener('DOMContentLoaded', function() {
    console.log('HealthyCareSystem JS loaded!');
    
    // Auto dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const dismissBtn = new bootstrap.Alert(alert);
            dismissBtn.close();
        });
    }, 5000);
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Appointment booking form validation
    const appointmentForm = document.getElementById('appointmentForm');
    if (appointmentForm) {
        appointmentForm.addEventListener('submit', function(e) {
            if (!appointmentForm.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            
            appointmentForm.classList.add('was-validated');
        });
    }
    
    // Doctor search filter
    const searchInput = document.getElementById('doctorSearch');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            const searchValue = this.value.toLowerCase();
            const doctorCards = document.querySelectorAll('.doctor-card');
            
            doctorCards.forEach(card => {
                const doctorName = card.querySelector('.doctor-name').textContent.toLowerCase();
                const specialization = card.querySelector('.doctor-specialization').textContent.toLowerCase();
                
                if (doctorName.includes(searchValue) || specialization.includes(searchValue)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    // Chatbot functionality
    const chatForm = document.getElementById('chatForm');
    const chatMessages = document.getElementById('chatMessages');
    
    if (chatForm && chatMessages) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (message) {
                // Add user message to chat
                addMessage(message, 'user');
                messageInput.value = '';
                
                // Scroll to bottom
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // This would normally connect to your WebSocket
                // For now, we'll just simulate a response
                setTimeout(function() {
                    const botResponses = [
                        "Xin chào! Tôi có thể giúp gì cho bạn?",
                        "Vui lòng mô tả triệu chứng của bạn chi tiết hơn để tôi có thể tư vấn tốt hơn.",
                        "Bạn nên đặt lịch khám với bác sĩ chuyên khoa để được tư vấn chính xác.",
                        "Tôi không phải là bác sĩ, nhưng tôi có thể giúp bạn tìm thông tin y tế cơ bản.",
                        "Đó có thể là triệu chứng của nhiều bệnh khác nhau. Bạn nên đi khám để được chẩn đoán chính xác."
                    ];
                    
                    const randomResponse = botResponses[Math.floor(Math.random() * botResponses.length)];
                    addMessage(randomResponse, 'bot');
                    
                    // Scroll to bottom again
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }, 1000);
            }
        });
        
        function addMessage(text, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', 'd-flex', 'mb-3');
            
            const innerDiv = document.createElement('div');
            innerDiv.classList.add(`message-${sender}`, 'rounded', 'p-3');
            innerDiv.textContent = text;
            
            messageDiv.appendChild(innerDiv);
            chatMessages.appendChild(messageDiv);
        }
    }
    
    // Calendar for appointment booking
    const appointmentCalendar = document.getElementById('appointmentCalendar');
    if (appointmentCalendar && typeof FullCalendar !== 'undefined') {
        const calendar = new FullCalendar.Calendar(appointmentCalendar, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: '/appointments/api/calendar-events/',
            eventClick: function(info) {
                if (info.event.url) {
                    window.location.href = info.event.url;
                    return false;
                }
            }
        });
        
        calendar.render();
    }
    
    // Rating system
    const ratingInputs = document.querySelectorAll('.rating input');
    if (ratingInputs.length > 0) {
        ratingInputs.forEach(input => {
            input.addEventListener('change', function() {
                const ratingValue = document.getElementById('ratingValue');
                if (ratingValue) {
                    ratingValue.textContent = this.value;
                }
            });
        });
    }
});
