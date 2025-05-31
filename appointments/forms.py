from django import forms
from .models import Review, Appointment
from doctors.models import Doctor

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }

class AppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Ngày hẹn"
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        label="Giờ hẹn"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        label="Lý do khám"
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.none(),  # Start with an empty queryset
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Chọn bác sĩ"
        # empty_label will be set in __init__
    )
    appointment_type = forms.ChoiceField(
        choices=Appointment.APPOINTMENT_TYPE_CHOICES, # Use choices from the model
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Loại khám"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        initial_doctor_instance = self.initial.get('doctor')
        
        base_queryset = Doctor.objects.filter(is_available=True)
        
        current_queryset = base_queryset
        if initial_doctor_instance:
            # If an initial doctor is provided, ensure they are part of the choices.
            # Union of available doctors and the specific initial doctor.
            current_queryset = base_queryset | Doctor.objects.filter(pk=initial_doctor_instance.pk)
            current_queryset = current_queryset.distinct()
        
        self.fields['doctor'].queryset = current_queryset

        if not self.fields['doctor'].queryset.exists():
            self.fields['doctor'].help_text = "Hiện không có bác sĩ nào để chọn."
            self.fields['doctor'].widget.attrs['disabled'] = True
            self.fields['doctor'].empty_label = "Không có bác sĩ"
            self.fields['doctor'].required = False # Not required if disabled and no choices
        else:
            self.fields['doctor'].empty_label = "--- Chọn bác sĩ ---" # Default for when there are choices
            self.fields['doctor'].required = True
            if initial_doctor_instance and not initial_doctor_instance.is_available:
                # Add a note if the pre-selected doctor is not generally available
                self.fields['doctor'].help_text = f"Lưu ý: BS. {initial_doctor_instance.user.get_full_name()} có thể không có trong danh sách tìm kiếm chung."


    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'reason', 'appointment_type'] # Added 'appointment_type'
