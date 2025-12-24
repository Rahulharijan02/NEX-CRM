"""
Tests verifying that creating an appointment sends an email to the patient.
"""

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from django.core import mail

from tenants.models import Tenant
from accounts.models import User
from clinic.models import Patient


class AppointmentEmailTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Tenant D')
        self.user = User.objects.create_user(username='userd', password='pass', tenant=self.tenant, role='practitioner')
        self.patient = Patient.objects.create(tenant=self.tenant, created_by=self.user, first_name='Daisy', last_name='Hill', email='daisy@hill.com')

    def test_email_sent_on_appointment_creation(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        payload = {
            'patient': self.patient.id,
            'practitioner': self.user.id,
            'reason': 'Routine checkup',
        }
        response = client.post(reverse('appointment-list'), data=payload)
        self.assertEqual(response.status_code, 201)
        # Ensure an email has been sent to the patient
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Appointment Confirmation', mail.outbox[0].subject)
        self.assertIn('Daisy', mail.outbox[0].body)