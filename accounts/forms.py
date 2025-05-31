from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=15, required=False)
    user_type = forms.ChoiceField(
        choices=[('patient', 'Bệnh nhân'), ('doctor', 'Bác sĩ')],
        widget=forms.RadioSelect,
        initial='patient'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'user_type', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = "Yêu cầu 150 ký tự hoặc ít hơn. Chỉ chấp nhận chữ cái, số và @/./+/-/_."
        self.fields['password1'].help_text = "Mật khẩu phải có ít nhất 8 ký tự và không được quá đơn giản."
        self.fields['first_name'].label = "Họ"
        self.fields['last_name'].label = "Tên"
        self.fields['email'].label = "Địa chỉ email"
        self.fields['phone'].label = "Số điện thoại"
        self.fields['user_type'].label = "Loại tài khoản"
        self.fields['password1'].label = "Mật khẩu"
        self.fields['password2'].label = "Xác nhận mật khẩu"
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Specific styling for radio buttons
        self.fields['user_type'].widget.attrs.update({'class': 'form-check-input'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data['phone']
        user.user_type = self.cleaned_data['user_type']
        
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, label="Họ")
    last_name = forms.CharField(max_length=30, required=True, label="Tên")
    email = forms.EmailField(required=True, label="Email")
    phone = forms.CharField(max_length=15, required=False, label="Số điện thoại")
    date_of_birth = forms.DateField(required=False, label="Ngày sinh", 
                                   widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(required=False, label="Địa chỉ", widget=forms.Textarea(attrs={'rows': 3}))
    avatar = forms.ImageField(required=False, label="Ảnh đại diện")
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'address', 'avatar')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        username = self.instance.username
        
        if User.objects.filter(email=email).exclude(username=username).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        
        return email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'avatar':
                field.widget.attrs.update({'class': 'form-control'})
            else:
                field.widget.attrs.update({'class': 'form-control-file'})
