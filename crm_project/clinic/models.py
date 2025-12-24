"""
Models for the clinic vertical application.

This module defines health‑care specific entities such as Patient and
Appointment. Each model inherits from TenantAwareModel to ensure that
data remains isolated per tenant.
"""

from __future__ import annotations

from django.db import models
from django.utils import timezone

from tenants.models import TenantAwareModel
from accounts.models import User


class Patient(TenantAwareModel):
    """Represents a patient in the clinic system."""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.first_name} {self.last_name}"


class Appointment(TenantAwareModel):
    """Represents an appointment scheduled between a patient and practitioner."""

    STATUS_SCHEDULED = 'scheduled'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    practitioner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    scheduled_at = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_appointments')

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Appointment with {self.patient} at {self.scheduled_at}"