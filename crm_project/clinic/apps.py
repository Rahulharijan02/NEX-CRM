"""
App configuration for the clinic vertical application.

This app provides health‑care specific functionality on top of the core
CRM, including models for patients and appointments.
"""

from django.apps import AppConfig


class ClinicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'clinic'
    verbose_name = 'Clinic'