from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('<int:doctor_id>/', views.doctor_detail, name='detail'),
    path('profile/', views.doctor_profile, name='profile'),
    path('schedule/', views.doctor_schedule, name='schedule'),
    path('specializations/', views.specialization_list, name='specializations'),
]
