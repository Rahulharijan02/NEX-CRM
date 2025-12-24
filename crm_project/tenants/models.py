"""
Models for the tenants application.

This module defines the core multi‑tenant entities used across the
platform. All tenant‑owned models should inherit from TenantAwareModel
to ensure a tenant foreign key is present on every row. A Tenant
represents a logical customer of the CRM platform (e.g. a clinic or
practice) and is used to scope data.
"""

from __future__ import annotations

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base class that tracks creation and update timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Tenant(models.Model):
    """Represents a tenant (organization) using the CRM platform."""

    name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class TenantAwareModel(TimeStampedModel):
    """Abstract base class for models bound to a tenant.

    All models inheriting from this class will include a foreign key
    pointing to the tenant that owns the record. Use this for any
    entity that should be scoped to a tenant, such as contacts,
    deals, patients, etc.
    """

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True