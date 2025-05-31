from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='list'),
    path('profile/', views.patient_profile, name='profile'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('medical-history/', views.medical_history, name='medical_history'),
    path('<int:patient_id>/', views.patient_detail, name='detail'),
]
