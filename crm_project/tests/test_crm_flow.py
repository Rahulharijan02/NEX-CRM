"""
Tests covering a typical CRM flow: creating a contact and a deal and
retrieving them via the API.
"""

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from tenants.models import Tenant
from accounts.models import User
from crm.models import Contact


class CRMFlowTests(APITestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Tenant C')
        self.user = User.objects.create_user(username='userc', password='pass', tenant=self.tenant)

    def test_create_contact_and_deal(self):
        client = APIClient()
        client.force_authenticate(user=self.user)
        # Create contact
        contact_payload = {
            'first_name': 'Charlie',
            'last_name': 'Brown',
            'email': 'charlie@brown.com',
            'phone': '789',
        }
        response = client.post(reverse('contact-list'), data=contact_payload)
        self.assertEqual(response.status_code, 201)
        contact_id = response.json()['id']
        # Create deal linked to contact
        deal_payload = {
            'name': 'Big Deal',
            'contact': contact_id,
            'amount': '5000.00',
            'stage': 'new',
            'description': 'Test deal',
        }
        response = client.post(reverse('deal-list'), data=deal_payload)
        self.assertEqual(response.status_code, 201)
        # Retrieve deals
        response = client.get(reverse('deal-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], 'Big Deal')