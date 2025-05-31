from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Appointment, MedicalRecord, Review, TimeSlot
from .serializers import AppointmentSerializer, MedicalRecordSerializer, ReviewSerializer, TimeSlotSerializer

class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Appointments
    """
    queryset = Appointment.objects.all()  # Add this line to fix the error
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'appointment_date']

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return Appointment.objects.filter(patient__user=user)
        elif user.user_type == 'doctor':
            return Appointment.objects.filter(doctor__user=user)
        else:
            return Appointment.objects.all()

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel appointment
        """
        appointment = self.get_object()
        if appointment.status not in ['cancelled', 'completed']:
            appointment.status = 'cancelled'
            appointment.save()
            return Response({'status': 'cancelled'})
        return Response({'error': 'Cannot cancel this appointment'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete appointment (doctors only)
        """
        if request.user.user_type != 'doctor':
            return Response({'error': 'Only doctors can complete appointments'}, status=status.HTTP_403_FORBIDDEN)
        
        appointment = self.get_object()
        appointment.status = 'completed'
        appointment.diagnosis = request.data.get('diagnosis', '')
        appointment.prescription = request.data.get('prescription', '')
        appointment.notes = request.data.get('notes', '')
        appointment.save()
        
        return Response({'status': 'completed'})

class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Medical Records
    """
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return MedicalRecord.objects.filter(appointment__patient__user=user)
        elif user.user_type == 'doctor':
            return MedicalRecord.objects.filter(appointment__doctor__user=user)
        else:
            return MedicalRecord.objects.all()

class ReviewViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Reviews
    """
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return Review.objects.filter(appointment__patient__user=user)
        else:
            return Review.objects.all()


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for TimeSlots
    """
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['doctor', 'date', 'is_available']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get available time slots for a doctor and date
        """
        doctor_id = request.query_params.get('doctor', None)
        date = request.query_params.get('date', None)
        
        if not doctor_id or not date:
            return Response({'error': 'Doctor ID and date are required'}, status=status.HTTP_400_BAD_REQUEST)
            
        slots = TimeSlot.objects.filter(doctor_id=doctor_id, date=date, is_available=True)
        serializer = self.get_serializer(slots, many=True)
        return Response(serializer.data)
