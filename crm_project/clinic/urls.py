"""
URL configuration for the clinic vertical application.

These routes power the HTML interface for managing patients and
appointments. API routes are registered centrally via the project
router. The app uses its own namespace 'clinic'.
"""

from django.urls import path

from . import views

app_name = 'clinic'

urlpatterns = [
    path('patients/', views.patient_list, name='patients'),
    path('patients/create/', views.patient_create, name='patient_create'),
    path('appointments/', views.appointment_list, name='appointments'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
]