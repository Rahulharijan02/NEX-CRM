"""
Serializers for the core CRM application.

These serializers convert model instances into JSON for the API and
validate incoming request payloads. They also set the tenant and
created_by fields automatically during creation to enforce multi‑tenant
isolation and audit metadata.
"""

from __future__ import annotations

from django.utils import timezone
from rest_framework import serializers

from .models import Contact, Deal, Activity


class ContactSerializer(serializers.ModelSerializer):
    """Serializer for the Contact model."""

    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'email', 'phone']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        return Contact.objects.create(
            tenant=user.tenant,
            created_by=user,
            **validated_data,
        )


class DealSerializer(serializers.ModelSerializer):
    """Serializer for the Deal model."""

    class Meta:
        model = Deal
        fields = ['id', 'name', 'contact', 'amount', 'stage', 'close_date', 'description']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        return Deal.objects.create(
            tenant=user.tenant,
            created_by=user,
            **validated_data,
        )


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer for the Activity model."""

    class Meta:
        model = Activity
        fields = ['id', 'type', 'title', 'description', 'due_date', 'completed', 'contact', 'deal']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        return Activity.objects.create(
            tenant=user.tenant,
            created_by=user,
            **validated_data,
        )