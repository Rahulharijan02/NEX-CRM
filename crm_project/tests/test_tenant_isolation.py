"""
Tests verifying that data is properly isolated between tenants.

These tests use Django's built‑in test client and DRF's APIClient to
assert that users cannot see or manipulate data belonging to another
tenant.
"""

from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from tenants.models import Tenant
from accounts.models import User
from crm.models import Contact, Deal


class TenantIsolationTests(APITestCase):
    def setUp(self):
        self.tenant1 = Tenant.objects.create(name='Tenant A')
        self.tenant2 = Tenant.objects.create(name='Tenant B')
        self.user1 = User.objects.create_user(username='user1', password='pass', tenant=self.tenant1)
        self.user2 = User.objects.create_user(username='user2', password='pass', tenant=self.tenant2)
        self.contact1 = Contact.objects.create(tenant=self.tenant1, first_name='Alice', last_name='Smith', email='alice@example.com', phone='123')
        self.contact2 = Contact.objects.create(tenant=self.tenant2, first_name='Bob', last_name='Jones', email='bob@example.com', phone='456')
        self.deal1 = Deal.objects.create(tenant=self.tenant1, name='Deal1', contact=self.contact1, amount=1000)
        self.deal2 = Deal.objects.create(tenant=self.tenant2, name='Deal2', contact=self.contact2, amount=2000)

    def test_contacts_are_tenant_isolated(self):
        client = APIClient()
        client.force_authenticate(user=self.user1)
        response = client.get(reverse('contact-list'))
        self.assertEqual(response.status_code, 200)
        # Only one contact should be returned for tenant1
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['email'], 'alice@example.com')

    def test_deals_are_tenant_isolated(self):
        client = APIClient()
        client.force_authenticate(user=self.user2)
        response = client.get(reverse('deal-list'))
        self.assertEqual(response.status_code, 200)
        # Only one deal should be returned for tenant2
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['name'], 'Deal2')