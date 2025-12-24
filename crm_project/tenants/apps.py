"""
App configuration for the tenants application.

The Tenants app holds the Tenant model and any related logic. A tenant
represents an organization using the CRM platform. All tenant‑owned
entities (contacts, deals, activities, patients, appointments) link to
Tenant via a foreign key to ensure data isolation in a multi‑tenant
setup.
"""

from django.apps import AppConfig


class TenantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenants'
    verbose_name = 'Tenants'