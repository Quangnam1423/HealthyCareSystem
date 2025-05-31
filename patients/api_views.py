from rest_framework import viewsets, permissions
from .models import Patient
from .serializers import PatientSerializer

class PatientViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Patients
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return Patient.objects.filter(user=user)
        elif user.user_type == 'doctor':
            # Doctors can see their patients
            return Patient.objects.filter(appointment__doctor__user=user).distinct()
        else:
            # Admin can see all
            return Patient.objects.all()
