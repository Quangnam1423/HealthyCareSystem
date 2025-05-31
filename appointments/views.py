from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Appointment, MedicalRecord, Review
from doctors.models import Doctor, Specialization # Add Specialization
from patients.models import Patient
from .forms import ReviewForm, AppointmentForm # Added AppointmentForm

@login_required
def appointment_list(request):
    """Danh sách lịch hẹn"""
    if request.user.user_type == 'patient':
        try:
            patient = request.user.patient
            appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-appointment_time')
        except Patient.DoesNotExist: # Changed from bare except
            messages.error(request, "Không tìm thấy thông tin bệnh nhân. Vui lòng cập nhật hồ sơ.")
            appointments = []
        except Exception as e: # Catch other potential errors
            messages.error(request, f"Đã có lỗi xảy ra khi tải lịch hẹn: {e}")
            appointments = []
    elif request.user.user_type == 'doctor':
        try:
            doctor = request.user.doctor
            appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', '-appointment_time')
        except Doctor.DoesNotExist: # Changed from bare except
            messages.error(request, "Không tìm thấy thông tin bác sĩ. Vui lòng cập nhật hồ sơ.")
            appointments = []
        except Exception as e: # Catch other potential errors
            messages.error(request, f"Đã có lỗi xảy ra khi tải lịch hẹn: {e}")
            appointments = []
    else: # Assuming admin or other roles that can see all
        appointments = Appointment.objects.all().order_by('-appointment_date', '-appointment_time')
    
    context = {'appointments': appointments}
    return render(request, 'appointments/appointment_list.html', context)

@login_required
def book_appointment(request):
    """Đặt lịch hẹn"""
    if request.user.user_type != 'patient':
        messages.error(request, 'Chỉ bệnh nhân mới có thể đặt lịch hẹn.')
        return redirect('core:home')
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist: # More specific exception
        messages.error(request, 'Vui lòng hoàn thiện thông tin bệnh nhân trước khi đặt lịch.')
        # Assuming you have a patient profile creation/edit page in the 'patients' app
        return redirect('patients:patient_profile_edit') # Or a relevant URL
    
    doctor_id = request.GET.get('doctor_id') # Get doctor_id from query params
    initial_data = {}
    selected_doctor_instance = None

    if doctor_id:
        try:
            selected_doctor_instance = Doctor.objects.get(id=doctor_id)
            initial_data['doctor'] = selected_doctor_instance
        except Doctor.DoesNotExist:
            messages.error(request, 'Bác sĩ không tồn tại.')
            # Consider redirecting to a doctor listing page or home
            # return redirect('doctors:list') 

    if request.method == 'POST':
        print(f"DEBUG: Received POST data: {request.POST}") # Debug print statement
        form = AppointmentForm(request.POST, initial=initial_data) 
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient 
            appointment.status = 'confirmed' # Changed from 'scheduled' to 'confirmed'
            
            # The form.cleaned_data['doctor'] should be set if validation passed.
            # If your JS submits 'doctor_id' in the POST body and your form's 'doctor' field
            # is correctly picking it up, this manual setting might not be strictly necessary
            # as form.save(commit=False) would have assigned it.
            # However, ensuring it's explicitly set from cleaned_data is robust.
            appointment.doctor = form.cleaned_data['doctor']
            
            appointment.save()
            messages.success(request, 'Đặt lịch thành công!')
            return redirect('appointments:list')
        else:
            messages.error(request, f"Vui lòng kiểm tra lại thông tin đặt lịch: {form.errors.as_json(escape_html=True)}") # Added form errors to message
            # Re-populate context for template re-rendering with form errors
            doctors_list = Doctor.objects.filter(is_available=True)
            if selected_doctor_instance: # If a doctor was initially targeted
                 # Ensure this doctor is in the list for display, regardless of current availability,
                 # as the form logic itself handles whether they are a valid choice.
                doctors_list = (doctors_list | Doctor.objects.filter(pk=selected_doctor_instance.pk)).distinct()

            specializations_list = Specialization.objects.all()
            context = {
                'form': form, 
                'doctors': doctors_list,
                'specializations': specializations_list,
                'selected_doctor_id': doctor_id # Pass original doctor_id for JS
            }
            return render(request, 'appointments/book_appointment.html', context)
    else: # GET request
        form = AppointmentForm(initial=initial_data)
        
        doctors_list = Doctor.objects.filter(is_available=True)
        if selected_doctor_instance:
            # If a specific doctor is pre-selected (e.g. from doctor_detail page),
            # ensure they are included in the list for the cards,
            # especially if they might not be in the general 'is_available=True' list.
            doctors_list = (doctors_list | Doctor.objects.filter(pk=selected_doctor_instance.pk)).distinct()

        specializations_list = Specialization.objects.all()

        context = {
            'form': form,
            'doctors': doctors_list,
            'specializations': specializations_list,
            'selected_doctor_id': doctor_id 
        }
        return render(request, 'appointments/book_appointment.html', context)

@login_required
def appointment_detail(request, appointment_id):
    """Chi tiết lịch hẹn"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Kiểm tra quyền truy cập
    if request.user.user_type == 'patient' and appointment.patient.user != request.user:
        messages.error(request, 'Bạn không có quyền xem lịch hẹn này.')
        return redirect('appointments:list')
    elif request.user.user_type == 'doctor' and appointment.doctor.user != request.user:
        messages.error(request, 'Bạn không có quyền xem lịch hẹn này.')
        return redirect('appointments:list')
    
    try:
        medical_record = appointment.medicalrecord
    except:
        medical_record = None
    
    context = {
        'appointment': appointment,
        'medical_record': medical_record,
    }
    return render(request, 'appointments/appointment_detail.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    """Hủy lịch hẹn"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Kiểm tra quyền hủy
    can_cancel = False
    if request.user.user_type == 'patient' and appointment.patient.user == request.user:
        can_cancel = True
    elif request.user.user_type == 'doctor' and appointment.doctor.user == request.user:
        can_cancel = True
    elif request.user.user_type == 'admin':
        can_cancel = True
    
    if not can_cancel:
        messages.error(request, 'Bạn không có quyền hủy lịch hẹn này.')
        return redirect('appointments:list')
    
    if appointment.status in ['cancelled', 'completed']:
        messages.error(request, 'Không thể hủy lịch hẹn này.')
        return redirect('appointments:detail', appointment_id=appointment.id)
    
    appointment.status = 'cancelled'
    appointment.save()
    
    messages.success(request, 'Lịch hẹn đã được hủy.')
    return redirect('appointments:list')

@login_required
def complete_appointment(request, appointment_id):
    """Hoàn thành lịch hẹn (chỉ dành cho bác sĩ)"""
    if request.user.user_type != 'doctor':
        messages.error(request, 'Chỉ bác sĩ mới có thể hoàn thành lịch hẹn.')
        return redirect('appointments:list')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.doctor.user != request.user:
        messages.error(request, 'Bạn không có quyền hoàn thành lịch hẹn này.')
        return redirect('appointments:list')
    
    if request.method == 'POST':
        appointment.status = 'completed'
        appointment.diagnosis = request.POST.get('diagnosis', '')
        appointment.prescription = request.POST.get('prescription', '')
        appointment.notes = request.POST.get('notes', '')
        appointment.save()
        
        messages.success(request, 'Hoàn thành lịch hẹn thành công.')
        return redirect('appointments:detail', appointment_id=appointment.id)
    
    context = {'appointment': appointment}
    return render(request, 'appointments/complete_appointment.html', context)

@login_required
def add_review(request, appointment_id):
    """Thêm đánh giá cho lịch hẹn đã hoàn thành (chỉ dành cho bệnh nhân)"""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if request.user.user_type != 'patient':
        messages.error(request, 'Chỉ bệnh nhân mới có thể thêm đánh giá.')
        return redirect('appointments:detail', appointment_id=appointment.id)
    
    try:
        patient = request.user.patient
    except Patient.DoesNotExist:
        messages.error(request, 'Thông tin bệnh nhân không tồn tại.')
        return redirect('core:home')

    if appointment.patient != patient:
        messages.error(request, 'Bạn không có quyền đánh giá lịch hẹn này.')
        return redirect('appointments:list')

    if appointment.status != 'completed':
        messages.error(request, 'Chỉ có thể đánh giá các lịch hẹn đã hoàn thành.')
        return redirect('appointments:detail', appointment_id=appointment.id)

    # Kiểm tra xem đã có đánh giá cho lịch hẹn này chưa
    existing_review = Review.objects.filter(appointment=appointment).first()
    if existing_review:
        messages.info(request, 'Bạn đã đánh giá lịch hẹn này rồi.')
        return redirect('appointments:detail', appointment_id=appointment.id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.appointment = appointment
            review.patient = patient
            review.doctor = appointment.doctor 
            review.save()
            messages.success(request, 'Cảm ơn bạn đã gửi đánh giá!')
            return redirect('appointments:detail', appointment_id=appointment.id)
        else:
            messages.error(request, 'Vui lòng sửa các lỗi trong biểu mẫu.')
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'appointment': appointment
    }
    return render(request, 'appointments/add_review.html', context)

@login_required
def appointment_calendar(request):
    """Lịch hẹn dạng calendar"""
    appointments = []
    
    if request.user.user_type == 'patient':
        try:
            patient = request.user.patient
            appointments = Appointment.objects.filter(patient=patient)
        except:
            pass
    elif request.user.user_type == 'doctor':
        try:
            doctor = request.user.doctor
            appointments = Appointment.objects.filter(doctor=doctor)
        except:
            pass
    else:
        appointments = Appointment.objects.all()
    
    context = {'appointments': appointments}
    return render(request, 'appointments/appointment_calendar.html', context)
