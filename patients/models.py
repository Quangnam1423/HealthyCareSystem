from django.db import models
from django.conf import settings

class Patient(models.Model):
    GENDER_CHOICES = [
        ('M', 'Nam'),
        ('F', 'Nữ'),
        ('O', 'Khác'),
    ]
    
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    patient_id = models.CharField(max_length=20, unique=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True, null=True)
    height = models.FloatField(blank=True, null=True, help_text="Chiều cao (cm)")
    weight = models.FloatField(blank=True, null=True, help_text="Cân nặng (kg)")
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True, help_text="Dị ứng")
    medical_history = models.TextField(blank=True, null=True, help_text="Tiền sử bệnh")
    current_medications = models.TextField(blank=True, null=True, help_text="Thuốc đang sử dụng")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.patient_id}"
    
    def save(self, *args, **kwargs):
        if not self.patient_id:
            # Tạo patient_id tự động
            from django.utils import timezone
            import random
            year = timezone.now().year
            random_num = random.randint(1000, 9999)
            self.patient_id = f"BN{year}{random_num}"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Bệnh nhân"
        verbose_name_plural = "Bệnh nhân"
