from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
]
