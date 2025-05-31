from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Patient
from appointments.models import Appointment

@login_required
def patient_list(request):
    """Danh sách bệnh nhân (chỉ dành cho bác sĩ và admin)"""
    if request.user.user_type not in ['doctor', 'admin']:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('core:home')
    
    patients = Patient.objects.all()
    return render(request, 'patients/patient_list.html', {'patients': patients})

@login_required
def patient_profile(request):
    """Thông tin cá nhân bệnh nhân"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Bạn không phải là bệnh nhân.')
        return redirect('core:home')
    
    try:
        patient = request.user.patient
    except:
        messages.error(request, 'Vui lòng hoàn thiện thông tin cá nhân.')
        return redirect('patients:edit_profile')
    
    recent_appointments = Appointment.objects.filter(patient=patient).order_by('-created_at')[:5]
    
    context = {
        'patient': patient,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'patients/patient_profile.html', context)

@login_required
def edit_profile(request):
    """Chỉnh sửa thông tin bệnh nhân"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Bạn không phải là bệnh nhân.')
        return redirect('core:home')
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        # Tạo hồ sơ bệnh nhân mới nếu chưa tồn tại
        patient = Patient(user=request.user)
    
    if request.method == 'POST':
        # Xử lý form cập nhật thông tin
        patient.gender = request.POST.get('gender')
        patient.blood_type = request.POST.get('blood_type')
        patient.height = request.POST.get('height')
        patient.weight = request.POST.get('weight')
        patient.emergency_contact_name = request.POST.get('emergency_contact_name')
        patient.emergency_contact_phone = request.POST.get('emergency_contact_phone')
        patient.allergies = request.POST.get('allergies')
        patient.medical_history = request.POST.get('medical_history')
        patient.current_medications = request.POST.get('current_medications')
        patient.save()
        
        # Cập nhật thông tin user
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.address = request.POST.get('address')
        
        # Xử lý cập nhật ngày sinh
        date_of_birth = request.POST.get('date_of_birth')
        if date_of_birth:
            user.date_of_birth = date_of_birth
            
        # Xử lý upload avatar
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        user.save()
        
        messages.success(request, 'Cập nhật thông tin thành công!')
        return redirect('patients:profile')
    
    context = {'patient': patient}
    return render(request, 'patients/edit_profile.html', context)

@login_required
def medical_history(request):
    """Lịch sử khám bệnh"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Bạn không phải là bệnh nhân.')
        return redirect('core:home')
    
    try:
        patient = request.user.patient
        appointments = Appointment.objects.filter(
            patient=patient, 
            status='completed'
        ).order_by('-appointment_date')
    except:
        appointments = []
    
    context = {'appointments': appointments}
    return render(request, 'patients/medical_history.html', context)

@login_required
def patient_detail(request, patient_id):
    """Chi tiết bệnh nhân (dành cho bác sĩ và admin)"""
    if request.user.user_type not in ['doctor', 'admin']:
        messages.error(request, 'Bạn không có quyền truy cập trang này.')
        return redirect('core:home')
    
    patient = get_object_or_404(Patient, id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    
    context = {
        'patient': patient,
        'appointments': appointments,
    }
    return render(request, 'patients/patient_detail.html', context)
