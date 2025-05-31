from django.db import models
from django.conf import settings
from patients.models import Patient
from doctors.models import Doctor

class TimeSlot(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.doctor} - {self.date} ({self.start_time}-{self.end_time})"
    
    class Meta:
        verbose_name = "Khung giờ"
        verbose_name_plural = "Khung giờ"
        unique_together = ['doctor', 'date', 'start_time']

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('in_progress', 'Đang khám'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('no_show', 'Không đến'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Tư vấn'),
        ('checkup', 'Khám tổng quát'),
        ('follow_up', 'Tái khám'),
        ('emergency', 'Cấp cứu'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(help_text="Lý do khám")
    notes = models.TextField(blank=True, null=True, help_text="Ghi chú từ bác sĩ")
    diagnosis = models.TextField(blank=True, null=True, help_text="Chẩn đoán")
    prescription = models.TextField(blank=True, null=True, help_text="Đơn thuốc")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.appointment_date} {self.appointment_time})"
    
    class Meta:
        verbose_name = "Lịch hẹn"
        verbose_name_plural = "Lịch hẹn"
        unique_together = ['doctor', 'appointment_date', 'appointment_time']

class MedicalRecord(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    symptoms = models.TextField(help_text="Triệu chứng")
    vital_signs = models.JSONField(blank=True, null=True, help_text="Các chỉ số sinh hiệu")
    lab_results = models.TextField(blank=True, null=True, help_text="Kết quả xét nghiệm")
    treatment_plan = models.TextField(blank=True, null=True, help_text="Kế hoạch điều trị")
    follow_up_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Hồ sơ bệnh án - {self.appointment}"
    
    class Meta:
        verbose_name = "Hồ sơ bệnh án"
        verbose_name_plural = "Hồ sơ bệnh án"

class Review(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Đánh giá {self.rating}/5 - {self.appointment.doctor}"
    
    class Meta:
        verbose_name = "Đánh giá"
        verbose_name_plural = "Đánh giá"
