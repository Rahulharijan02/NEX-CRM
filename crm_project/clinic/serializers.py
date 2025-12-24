"""
Serializers for the clinic vertical application.

These serializers convert Patient and Appointment model instances into
JSON and validate incoming API payloads. They automatically set the
tenant and created_by fields on creation to ensure multi‑tenant
integrity and audit trails.
"""

from __future__ import annotations

from rest_framework import serializers

from .models import Patient, Appointment


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for the Patient model."""

    class Meta:
        model = Patient
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        return Patient.objects.create(
            tenant=user.tenant,
            created_by=user,
            **validated_data,
        )


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for the Appointment model."""

    class Meta:
        model = Appointment
        fields = ['id', 'patient', 'practitioner', 'scheduled_at', 'reason', 'status']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        appointment = Appointment.objects.create(
            tenant=user.tenant,
            created_by=user,
            **validated_data,
        )
        # Send a confirmation email to the patient
        from django.core.mail import send_mail  # imported here to avoid circular import
        if appointment.patient.email:
            send_mail(
                subject='Appointment Confirmation',
                message=f"Dear {appointment.patient.first_name}, your appointment is scheduled at {appointment.scheduled_at}.",
                from_email=None,
                recipient_list=[appointment.patient.email],
                fail_silently=True,
            )
        return appointment