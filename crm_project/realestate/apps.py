"""
App configuration for the real estate vertical application.

This app provides real estate specific functionality on top of the core
CRM, including models for properties and viewings.
"""

from django.apps import AppConfig


class RealEstateConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'realestate'
    verbose_name = 'Real Estate'