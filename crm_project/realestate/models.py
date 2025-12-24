"""
Models for the real estate vertical application.

This module defines real estate specific entities such as Property and
Viewing. Each model inherits from TenantAwareModel to ensure that
data remains isolated per tenant.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone

from tenants.models import TenantAwareModel
from accounts.models import User
from crm.models import Contact


class Property(TenantAwareModel):
    """Represents a real estate property in the system."""

    STATUS_LISTED = 'listed'
    STATUS_SOLD = 'sold'
    STATUS_LET = 'let'
    STATUS_CHOICES = [
        (STATUS_LISTED, 'Listed'),
        (STATUS_SOLD, 'Sold'),
        (STATUS_LET, 'Let'),
    ]

    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_LISTED)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Viewing(TenantAwareModel):
    """Represents a viewing appointment of a property by a contact."""

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='viewings')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='viewings')
    scheduled_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Viewing of {self.property.name} with {self.contact}"