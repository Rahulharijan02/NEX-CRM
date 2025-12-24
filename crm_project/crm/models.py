"""
Models for the core CRM application.

This module defines the primary CRM entities: Contact, Deal and
Activity. Each model inherits from TenantAwareModel to ensure proper
tenant scoping. Relationships between models reflect typical CRM
workflows (e.g. deals linked to contacts).
"""

from __future__ import annotations

from decimal import Decimal
from django.db import models
from django.utils import timezone

from tenants.models import TenantAwareModel
from accounts.models import User


class Contact(TenantAwareModel):
    """Represents a person or organisation contact within the CRM."""

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"{self.first_name} {self.last_name}"


class Deal(TenantAwareModel):
    """Represents a sales opportunity or deal linked to a contact."""

    STAGE_NEW = 'new'
    STAGE_IN_PROGRESS = 'in_progress'
    STAGE_WON = 'won'
    STAGE_LOST = 'lost'
    STAGE_CHOICES = [
        (STAGE_NEW, 'New'),
        (STAGE_IN_PROGRESS, 'In Progress'),
        (STAGE_WON, 'Won'),
        (STAGE_LOST, 'Lost'),
    ]

    name = models.CharField(max_length=255)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='deals')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default=STAGE_NEW)
    close_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.name


class Activity(TenantAwareModel):
    """Represents an activity (task, note, etc.) linked to contacts and deals."""

    TYPE_TASK = 'task'
    TYPE_NOTE = 'note'
    TYPE_MEETING = 'meeting'
    TYPE_CHOICES = [
        (TYPE_TASK, 'Task'),
        (TYPE_NOTE, 'Note'),
        (TYPE_MEETING, 'Meeting'),
    ]

    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default=TYPE_TASK)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    due_date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    deal = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['completed', 'due_date']

    def __str__(self) -> str:  # pragma: no cover - trivial
        return self.title