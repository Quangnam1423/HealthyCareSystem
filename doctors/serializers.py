from rest_framework import serializers
from .models import Doctor, Specialization, DoctorSchedule
from accounts.serializers import UserSerializer

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ['id', 'name', 'description']

class DoctorScheduleSerializer(serializers.ModelSerializer):
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = DoctorSchedule
        fields = ['id', 'day_of_week', 'day_of_week_display', 'start_time', 'end_time', 'is_available']

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)
    schedules = DoctorScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Doctor
        fields = [
            'id', 'user', 'doctor_id', 'specializations', 'license_number',
            'years_of_experience', 'education', 'bio', 'consultation_fee',
            'is_available', 'rating', 'total_reviews', 'schedules'
        ]
        read_only_fields = ['doctor_id', 'rating', 'total_reviews']
