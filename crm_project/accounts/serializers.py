"""
Serializers for the accounts application.

These serializers convert User model instances into JSON and validate
incoming payloads. The UserSerializer is used by the UserViewSet to
expose user data via the API.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the custom User model."""

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'tenant']
        read_only_fields = ['id']