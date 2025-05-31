from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('', views.appointment_list, name='list'),
    path('book/', views.book_appointment, name='book'),
    path('<int:appointment_id>/', views.appointment_detail, name='detail'),
    path('<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel'),
    path('<int:appointment_id>/complete/', views.complete_appointment, name='complete'),
    path('<int:appointment_id>/review/', views.add_review, name='add_review'),  # Added this line
    path('calendar/', views.appointment_calendar, name='calendar'),
]
