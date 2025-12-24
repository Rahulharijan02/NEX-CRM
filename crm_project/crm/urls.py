"""
URL configuration for the core CRM application.

These routes power the basic HTML interface for managing contacts and
deals. API routes are handled centrally via the project's router and
registered in config/urls.py.
"""

from django.urls import path

from . import views

app_name = 'crm'

urlpatterns = [
    path('contacts/', views.contact_list, name='contacts'),
    path('contacts/create/', views.contact_create, name='contact_create'),
    path('deals/', views.deal_list, name='deals'),
    path('deals/create/', views.deal_create, name='deal_create'),
]