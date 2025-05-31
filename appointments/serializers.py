from rest_framework import serializers
from .models import Appointment, MedicalRecord, Review, TimeSlot
from patients.serializers import PatientSerializer
from doctors.serializers import DoctorSerializer

class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    doctor = DoctorSerializer(read_only=True)
    patient_id = serializers.IntegerField(write_only=True)
    doctor_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    appointment_type_display = serializers.CharField(source='get_appointment_type_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'doctor', 'patient_id', 'doctor_id',
            'appointment_date', 'appointment_time', 'appointment_type', 
            'appointment_type_display', 'status', 'status_display',
            'reason', 'notes', 'diagnosis', 'prescription', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class MedicalRecordSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'appointment', 'symptoms', 'vital_signs', 'lab_results',
            'treatment_plan', 'follow_up_date', 'created_at', 'updated_at'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    appointment = AppointmentSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'appointment', 'rating', 'comment', 'created_at']

class TimeSlotSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    
    class Meta:
        model = TimeSlot
        fields = ['id', 'doctor', 'doctor_name', 'date', 'start_time', 'end_time', 'is_available']
