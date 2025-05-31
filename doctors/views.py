from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import Doctor, Specialization, DoctorSchedule
from appointments.models import Appointment

def doctor_list(request):
    """Danh sách bác sĩ"""
    specialization_id = request.GET.get('specialization')
    search = request.GET.get('search')
    
    doctors = Doctor.objects.filter(is_available=True)
    
    if specialization_id:
        doctors = doctors.filter(specializations__id=specialization_id)
    
    if search:
        doctors = doctors.filter(
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(specializations__name__icontains=search)
        ).distinct()
    
    specializations = Specialization.objects.all()
    
    context = {
        'doctors': doctors,
        'specializations': specializations,
        'selected_specialization': specialization_id,
        'search': search,
    }
    return render(request, 'doctors/doctor_list.html', context)

def doctor_detail(request, doctor_id):
    """Chi tiết thông tin bác sĩ"""
    doctor = get_object_or_404(Doctor, id=doctor_id, is_available=True)
    schedules = DoctorSchedule.objects.filter(doctor=doctor, is_available=True)
    
    context = {
        'doctor': doctor,
        'schedules': schedules,
    }
    return render(request, 'doctors/doctor_detail.html', context)

@login_required
def doctor_profile(request):
    """Thông tin cá nhân bác sĩ"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Bạn không phải là bác sĩ.')
        return redirect('home')  # Changed from 'core:home'
    
    try:
        doctor = request.user.doctor
    except:
        messages.error(request, 'Vui lòng hoàn thiện thông tin bác sĩ.')
        return redirect('home')  # Changed from 'core:home'
    
    today_appointments = Appointment.objects.filter(
        doctor=doctor,
        appointment_date__date=timezone.now().date()
    ).order_by('appointment_time')
    
    context = {
        'doctor': doctor,
        'today_appointments': today_appointments,
    }
    return render(request, 'doctors/doctor_profile.html', context)

@login_required
def doctor_schedule(request):
    """Lịch làm việc của bác sĩ"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Bạn không phải là bác sĩ.')
        return redirect('home')  # Changed from 'core:home'
    
    try:
        doctor = request.user.doctor
        schedules = DoctorSchedule.objects.filter(doctor=doctor)
    except:
        schedules = []
    
    context = {'schedules': schedules}
    return render(request, 'doctors/doctor_schedule.html', context)

def specialization_list(request):
    """Danh sách chuyên khoa"""
    specializations = Specialization.objects.all()
    context = {'specializations': specializations}
    return render(request, 'doctors/specialization_list.html', context)
