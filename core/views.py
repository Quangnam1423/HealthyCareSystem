from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime, timedelta

from doctors.models import Doctor, Specialization
from appointments.models import Appointment
from patients.models import Patient

class HomeView(TemplateView):
    template_name = 'core/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Thống kê tổng quan
        context['total_doctors'] = Doctor.objects.filter(is_available=True).count()
        context['total_specializations'] = Specialization.objects.count()
        context['total_patients'] = Patient.objects.count()
        context['total_appointments_today'] = Appointment.objects.filter(
            appointment_date=datetime.now().date()
        ).count()
        
        # Các chuyên khoa
        context['specializations'] = Specialization.objects.all()[:6]
        
        # Bác sĩ nổi bật
        context['featured_doctors'] = Doctor.objects.filter(
            is_available=True
        ).order_by('-rating')[:6]
        
        return context

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.user_type == 'patient':
            try:
                patient = user.patient
                context['recent_appointments'] = Appointment.objects.filter(
                    patient=patient
                ).order_by('-created_at')[:5]
                context['upcoming_appointments'] = Appointment.objects.filter(
                    patient=patient,
                    appointment_date__gte=datetime.now().date(),
                    status__in=['pending', 'confirmed']
                ).order_by('appointment_date', 'appointment_time')[:3]
            except Patient.DoesNotExist:
                context['recent_appointments'] = []
                context['upcoming_appointments'] = []
                
        elif user.user_type == 'doctor':
            try:
                doctor = user.doctor
                today = datetime.now().date()
                context['today_appointments'] = Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=today
                ).order_by('appointment_time')
                context['pending_appointments'] = Appointment.objects.filter(
                    doctor=doctor,
                    status='pending'
                ).count()
                context['completed_today'] = Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=today,
                    status='completed'
                ).count()
            except Doctor.DoesNotExist:
                context['today_appointments'] = []
                context['pending_appointments'] = 0
                context['completed_today'] = 0
        
        return context

@login_required
def profile_view(request):
    """View hiển thị và chỉnh sửa profile người dùng"""
    user = request.user
    context = {'user': user}
    
    if user.user_type == 'patient':
        try:
            context['patient'] = user.patient
        except Patient.DoesNotExist:
            context['patient'] = None
    elif user.user_type == 'doctor':
        try:
            context['doctor'] = user.doctor
        except Doctor.DoesNotExist:
            context['doctor'] = None
    
    return render(request, 'core/profile.html', context)

def about_view(request):
    """Trang giới thiệu"""
    return render(request, 'core/about.html')

def contact_view(request):
    """Trang liên hệ"""
    if request.method == 'POST':
        # Xử lý form liên hệ
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # TODO: Gửi email hoặc lưu vào database
        messages.success(request, 'Cảm ơn bạn đã liên hệ. Chúng tôi sẽ phản hồi sớm nhất!')
        return redirect('contact')
    
    return render(request, 'core/contact.html')
