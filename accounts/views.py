from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.views.generic import CreateView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required

from .models import User
from .forms import UserRegistrationForm, ProfileUpdateForm
from patients.models import Patient
from doctors.models import Doctor
from appointments.models import Appointment

class RegisterView(CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Tạo đối tượng Patient hoặc Doctor tương ứng
        user = form.instance
        if user.user_type == 'patient':
            Patient.objects.create(user=user)
        elif user.user_type == 'doctor':
            Doctor.objects.create(user=user)
        
        messages.success(self.request, "Đăng ký thành công! Vui lòng đăng nhập.")
        return response
        
        # Tạo profile tương ứng
        user = self.object
        if user.user_type == 'patient':
            Patient.objects.create(user=user)
        elif user.user_type == 'doctor':
            # Doctor profile sẽ được tạo sau khi admin phê duyệt
            pass
            
        messages.success(self.request, 'Đăng ký thành công! Vui lòng đăng nhập.')
        return response

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Xin chào {user.get_full_name() or user.username}, đã đăng nhập thành công!")
                
                # Chuyển hướng tùy theo loại tài khoản
                if user.user_type == 'patient':
                    return redirect('patients:profile')
                elif user.user_type == 'doctor':
                    return redirect('doctors:profile')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Tên đăng nhập hoặc mật khẩu không hợp lệ!")
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không hợp lệ!")
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Đã đăng xuất thành công!")
    return redirect('home')

@login_required
def profile_view(request):
    user = request.user
    context = {'user': user}
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Thông tin cá nhân đã được cập nhật thành công!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Có lỗi xảy ra, vui lòng kiểm tra lại thông tin.")
    
    # Dữ liệu bổ sung cho profile
    if user.user_type == 'patient':
        try:
            patient = user.patient
            recent_appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-appointment_time')[:5]
            context.update({
                'patient': patient,
                'recent_appointments': recent_appointments
            })
        except:
            pass
    elif user.user_type == 'doctor':
        try:
            from django.utils import timezone
            doctor = user.doctor
            today_appointments = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=timezone.now().date()
            ).order_by('appointment_time')
            context.update({
                'doctor': doctor,
                'today_appointments': today_appointments
            })
        except:
            pass
    
    return render(request, 'accounts/profile.html', context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Cập nhật session để không bị logout
            update_session_auth_hash(request, user)
            messages.success(request, 'Mật khẩu của bạn đã được thay đổi thành công!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Vui lòng sửa lỗi dưới đây.')
            for error in form.errors:
                messages.error(request, form.errors[error])
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})
