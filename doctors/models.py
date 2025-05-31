from django.db import models
from django.conf import settings

class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Chuyên khoa"
        verbose_name_plural = "Chuyên khoa"

class Doctor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor_id = models.CharField(max_length=20, unique=True)
    specializations = models.ManyToManyField(Specialization)
    license_number = models.CharField(max_length=50, unique=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    education = models.TextField(help_text="Trình độ học vấn")
    bio = models.TextField(blank=True, null=True, help_text="Tiểu sử")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"BS. {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.doctor_id:
            # Tạo doctor_id tự động
            from django.utils import timezone
            import random
            year = timezone.now().year
            random_num = random.randint(1000, 9999)
            self.doctor_id = f"BS{year}{random_num}"
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Bác sĩ"
        verbose_name_plural = "Bác sĩ"

class DoctorSchedule(models.Model):
    WEEKDAYS = [
        (0, 'Thứ 2'),
        (1, 'Thứ 3'),
        (2, 'Thứ 4'),
        (3, 'Thứ 5'),
        (4, 'Thứ 6'),
        (5, 'Thứ 7'),
        (6, 'Chủ nhật'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.IntegerField(choices=WEEKDAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.doctor} - {self.get_day_of_week_display()} ({self.start_time} - {self.end_time})"
    
    class Meta:
        verbose_name = "Lịch làm việc"
        verbose_name_plural = "Lịch làm việc"
        unique_together = ['doctor', 'day_of_week', 'start_time']
