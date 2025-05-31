from rest_framework import serializers
from .models import Patient
from accounts.serializers import UserSerializer

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user', 'patient_id', 'gender', 'blood_type', 'height', 'weight',
            'emergency_contact_name', 'emergency_contact_phone', 'allergies',
            'medical_history', 'current_medications'
        ]
        read_only_fields = ['patient_id']
