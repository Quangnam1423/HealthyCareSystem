from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import API viewsets từ các apps
from doctors.api_views import DoctorViewSet, SpecializationViewSet
from patients.api_views import PatientViewSet
from appointments.api_views import AppointmentViewSet, TimeSlotViewSet
from chatbot.api_views import ChatSessionViewSet, ChatMessageViewSet, HealthSymptomViewSet

router = DefaultRouter()
router.register(r'doctors', DoctorViewSet)
router.register(r'specializations', SpecializationViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'appointments', AppointmentViewSet)
router.register(r'time-slots', TimeSlotViewSet)
router.register(r'chat-sessions', ChatSessionViewSet)
router.register(r'chat-messages', ChatMessageViewSet)
router.register(r'health-symptoms', HealthSymptomViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
