from django.contrib import admin
from .models import Doctor, Specialization, DoctorSchedule

@admin.register(Specialization)
class SpecializationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'doctor_id', 'get_specializations', 'years_of_experience', 'rating', 'is_available')
    list_filter = ('is_available', 'specializations', 'years_of_experience')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'doctor_id')
    filter_horizontal = ('specializations',)
    readonly_fields = ('doctor_id',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Họ tên'
    
    def get_specializations(self, obj):
        return ", ".join([s.name for s in obj.specializations.all()])
    get_specializations.short_description = 'Chuyên khoa'

@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'get_day_of_week_display', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available', 'doctor')
    search_fields = ('doctor__user__first_name', 'doctor__user__last_name')
