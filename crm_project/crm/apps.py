"""
App configuration for the core CRM application.

The CRM app contains the primary data models for Contacts, Deals and
Activities. These models form the foundation of the CRM and link to
tenants and users for proper scoping.
"""

from django.apps import AppConfig


class CrmConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crm'
    verbose_name = 'CRM'