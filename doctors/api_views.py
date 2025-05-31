from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Doctor, Specialization, DoctorSchedule
from .serializers import DoctorSerializer, SpecializationSerializer, DoctorScheduleSerializer

class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Specializations - Read only
    """
    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer
    permission_classes = [permissions.AllowAny]

class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Doctors - Read only
    """
    queryset = Doctor.objects.filter(is_available=True)
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['specializations', 'is_available']
    search_fields = ['user__first_name', 'user__last_name', 'specializations__name']
    ordering_fields = ['rating', 'years_of_experience', 'consultation_fee']
    ordering = ['-rating']

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """
        Get doctor's schedule
        """
        doctor = self.get_object()
        schedules = DoctorSchedule.objects.filter(doctor=doctor, is_available=True)
        serializer = DoctorScheduleSerializer(schedules, many=True)
        return Response(serializer.data)
