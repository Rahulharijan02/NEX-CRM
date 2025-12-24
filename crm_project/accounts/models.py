"""
Custom user model for the accounts application.

The User model extends Django's AbstractUser to include a foreign key
to the tenant that owns the user, as well as a simple role field used
for role‑based access control. See README.md for an overview of the
available roles and their permissions.
"""

from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models

from tenants.models import Tenant


class User(AbstractUser):
    """Custom user model linking a user to a tenant and a role."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, null=True, blank=True)

    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_AGENT = 'agent'
    ROLE_PRACTITIONER = 'practitioner'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MANAGER, 'Manager'),
        (ROLE_AGENT, 'Agent'),
        (ROLE_PRACTITIONER, 'Practitioner'),
    ]

    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default=ROLE_AGENT)

    def __str__(self) -> str:  
        return self.username