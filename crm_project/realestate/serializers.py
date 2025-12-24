"""
Serializers for the real estate vertical application.

These serializers convert Property and Viewing model instances into
JSON and validate incoming API payloads. They automatically set the
tenant and created_by fields on creation to ensure multi‑tenant
integrity and audit trails.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import Property, Viewing


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for the Property model."""

    class Meta:
        model = Property
        fields = ['id', 'name', 'address', 'city', 'status', 'description', 'price']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        return Property.objects.create(
            tenant=user.tenant,
            created_by=user,
            **validated_data,
        )


class ViewingSerializer(serializers.ModelSerializer):
    """Serializer for the Viewing model."""

    class Meta:
        model = Viewing
        fields = ['id', 'property', 'contact', 'scheduled_at', 'notes']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        return Viewing.objects.create(
            tenant=user.tenant,
            created_by=user,
            **validated_data,
        )