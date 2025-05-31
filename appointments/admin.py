from django.contrib import admin
from .models import Appointment, MedicalRecord, Review

class MedicalRecordInline(admin.StackedInline):
    model = MedicalRecord
    can_delete = False
    extra = 0
    
class ReviewInline(admin.StackedInline):
    model = Review
    can_delete = False
    extra = 0

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_doctor_name', 'appointment_date', 'appointment_time', 'appointment_type', 'status')
    list_filter = ('status', 'appointment_type', 'appointment_date')
    search_fields = ('patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name', 'doctor__user__last_name')
    date_hierarchy = 'appointment_date'
    inlines = [MedicalRecordInline, ReviewInline]
    
    def get_patient_name(self, obj):
        return obj.patient.user.get_full_name()
    get_patient_name.short_description = 'Bệnh nhân'
    
    def get_doctor_name(self, obj):
        return obj.doctor.user.get_full_name()
    get_doctor_name.short_description = 'Bác sĩ'

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_doctor_name', 'get_appointment_date', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('appointment__patient__user__first_name', 'appointment__patient__user__last_name')
    readonly_fields = ('appointment',)
    
    def get_patient_name(self, obj):
        return obj.appointment.patient.user.get_full_name()
    get_patient_name.short_description = 'Bệnh nhân'
    
    def get_doctor_name(self, obj):
        return obj.appointment.doctor.user.get_full_name()
    get_doctor_name.short_description = 'Bác sĩ'
    
    def get_appointment_date(self, obj):
        return obj.appointment.appointment_date
    get_appointment_date.short_description = 'Ngày khám'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_patient_name', 'get_doctor_name', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('appointment__patient__user__first_name', 'appointment__patient__user__last_name')
    readonly_fields = ('appointment',)
    
    def get_patient_name(self, obj):
        return obj.appointment.patient.user.get_full_name()
    get_patient_name.short_description = 'Bệnh nhân'
    
    def get_doctor_name(self, obj):
        return obj.appointment.doctor.user.get_full_name()
    get_doctor_name.short_description = 'Bác sĩ'
