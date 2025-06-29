# Generated by Django 5.2.1 on 2025-05-27 03:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctors', '0001_initial'),
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField()),
                ('appointment_type', models.CharField(choices=[('consultation', 'Tư vấn'), ('checkup', 'Khám tổng quát'), ('follow_up', 'Tái khám'), ('emergency', 'Cấp cứu')], max_length=20)),
                ('status', models.CharField(choices=[('pending', 'Chờ xác nhận'), ('confirmed', 'Đã xác nhận'), ('in_progress', 'Đang khám'), ('completed', 'Hoàn thành'), ('cancelled', 'Đã hủy'), ('no_show', 'Không đến')], default='pending', max_length=20)),
                ('reason', models.TextField(help_text='Lý do khám')),
                ('notes', models.TextField(blank=True, help_text='Ghi chú từ bác sĩ', null=True)),
                ('diagnosis', models.TextField(blank=True, help_text='Chẩn đoán', null=True)),
                ('prescription', models.TextField(blank=True, help_text='Đơn thuốc', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctors.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patient')),
            ],
            options={
                'verbose_name': 'Lịch hẹn',
                'verbose_name_plural': 'Lịch hẹn',
                'unique_together': {('doctor', 'appointment_date', 'appointment_time')},
            },
        ),
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symptoms', models.TextField(help_text='Triệu chứng')),
                ('vital_signs', models.JSONField(blank=True, help_text='Các chỉ số sinh hiệu', null=True)),
                ('lab_results', models.TextField(blank=True, help_text='Kết quả xét nghiệm', null=True)),
                ('treatment_plan', models.TextField(blank=True, help_text='Kế hoạch điều trị', null=True)),
                ('follow_up_date', models.DateField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='appointments.appointment')),
            ],
            options={
                'verbose_name': 'Hồ sơ bệnh án',
                'verbose_name_plural': 'Hồ sơ bệnh án',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)])),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='appointments.appointment')),
            ],
            options={
                'verbose_name': 'Đánh giá',
                'verbose_name_plural': 'Đánh giá',
            },
        ),
    ]
