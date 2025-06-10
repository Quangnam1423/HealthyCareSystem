// HealthyCare System Custom JavaScript

// Initialize Bootstrap tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Chat functionality
class ChatBot {    constructor(sessionId, csrfToken) { // Added csrfToken
        this.sessionId = sessionId || ''; 
        if (!this.sessionId) {
            console.error("ChatBot initialized without a session ID!");
            // Potentially generate one client-side or handle error
            // For now, we assume chat_session.html always provides it.
        }
        this.csrfToken = csrfToken; // Store CSRF token
        this.messagesContainer = document.getElementById('chatHistory'); // Changed from 'chat-messages' to 'chatHistory'
        this.messageInput = document.getElementById('messageInput'); // Corrected ID
        this.sendButton = document.getElementById('send-button'); // Ensure this ID exists or use the form's submit
        
        this.bindEvents();
        this.setConnectionStatus(true); // Assume "connected" for HTTP model
    }

    bindEvents() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => {
                this.sendMessage();
            });
        }
        
        if (this.messageInput) {
            this.messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }

    async sendMessage() { // Made async for await fetch
        const messageText = this.messageInput.value.trim(); // Renamed for clarity

        if (!messageText) {
            return; // Don't send empty messages
        }

        if (!this.sessionId) {
            console.error("Cannot send message, session ID is missing.");
            showNotification("Lỗi: Không tìm thấy ID phiên chat. Vui lòng làm mới trang.", "danger");
            return;
        }
        
        this.messageInput.value = '';
        this.showTypingIndicator(); // Show typing indicator for bot

        try {
            const response = await fetch('/chatbot/api/chatbot/message/', { // <-- UPDATED URL
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken 
                },
                body: JSON.stringify({
                    'message': messageText,
                    'session_id': this.sessionId 
                })
            });

            this.hideTypingIndicator();

            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    errorData = { error: `HTTP error! status: ${response.status}` };
                }
                console.error("Error sending message:", errorData);
                showNotification(`Lỗi gửi tin nhắn: ${errorData.error || response.statusText}`, 'danger');
                this.messageInput.value = messageText; 
                return;
            }

            const data = await response.json();

            if (data.success) {
                if (data.user_message) {
                     this.displayMessage(data.user_message.message, data.user_message.sender, data.user_message.type, data.user_message.timestamp);
                }
                if (data.bot_message) {
                    this.displayMessage(data.bot_message.message, data.bot_message.sender, data.bot_message.type, data.bot_message.timestamp);
                }
                if (data.session_id && (!this.sessionId || this.sessionId !== data.session_id)) { 
                    this.sessionId = data.session_id;
                    console.log(`Session ID updated/confirmed by server: ${this.sessionId}`);
                }
            } else {
                console.error("Error from server:", data.error);
                showNotification(`Lỗi từ server: ${data.error || 'Không rõ lỗi'}`, 'danger');
                this.messageInput.value = messageText; 
            }

        } catch (error) {
            this.hideTypingIndicator();
            console.error("Network error or other issue sending message:", error);
            showNotification('Lỗi mạng hoặc không thể kết nối tới server.', 'danger');
            this.messageInput.value = messageText; 
        }
    }

    displayMessage(message, sender, type, timestamp) {
        this.hideTypingIndicator();
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        bubbleDiv.innerHTML = this.formatMessage(message);
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = this.formatTime(timestamp);
        
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(timeDiv);
        
        if (this.messagesContainer) {
            this.messagesContainer.appendChild(messageDiv);
            this.scrollToBottom();
        }
    }

    formatMessage(message) {
        // Convert line breaks to <br> tags
        return message.replace(/\n/g, '<br>');
    }

    formatTime(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleTimeString('vi-VN', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message bot';
        typingDiv.innerHTML = `
            <div class="message-bubble">
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        if (this.messagesContainer) {
            this.messagesContainer.appendChild(typingDiv);
            this.scrollToBottom();
        }
    }

    hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }

    setConnectionStatus(connected) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            // For non-WebSocket, "connection" is more about ability to send/receive via HTTP
            // We can simplify this or remove it. For now, keep UI consistent.
            statusElement.textContent = connected ? 'Sẵn sàng' : 'Không thể kết nối'; 
            statusElement.className = connected ? 'text-success' : 'text-danger';
        }
        
        if (this.sendButton) {
            this.sendButton.disabled = !connected;
        }
        
        if (this.messageInput) {
            this.messageInput.disabled = !connected;
        }
    }
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    const requiredFields = form.querySelectorAll('[required]');
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Date formatting
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Time formatting
function formatTime(timeString) {
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString('vi-VN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// AJAX form submission
function submitFormAjax(formId, successCallback, errorCallback) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    const url = form.action || window.location.href;
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (successCallback) successCallback(data);
        } else {
            if (errorCallback) errorCallback(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (errorCallback) errorCallback({error: 'Có lỗi xảy ra'});
    });
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show loading spinner
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div class="loading-spinner"></div> Đang tải...';
        element.disabled = true;
    }
}

// Hide loading spinner
function hideLoading(elementId, originalText) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notificationDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notificationDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notificationDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notificationDiv.parentNode) {
            notificationDiv.remove();
        }
    }, 5000);
}

// Export functions for global use
window.HealthyCare = {
    ChatBot,
    validateForm,
    formatDate,
    formatTime,
    submitFormAjax,
    getCookie,
    showLoading,
    hideLoading,
    showNotification
};
