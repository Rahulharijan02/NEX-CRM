"""Create demo users + sample data (safe to run once)."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from tenants.models import Tenant
from crm.models import Contact, Deal
from clinic.models import Patient, Appointment
from realestate.models import Property, Viewing


class Command(BaseCommand):
    help = "Create demo tenant, users, and sample data."

    def handle(self, *args, **options):
        User = get_user_model()

        # If demo already exists, do nothing
        if User.objects.filter(username="admin").exists():
            self.stdout.write(self.style.WARNING("Demo data already exists (user 'admin' found)."))
            return

        tenant = Tenant.objects.create(name="Demo Organisation")

        # Create one account per role for easy RBAC testing
        admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="admin123",
            tenant=tenant,
            role="admin",
        )

        manager = User.objects.create_user(
            username="manager",
            email="manager@example.com",
            password="manager123",
            tenant=tenant,
            role="manager",
        )

        agent = User.objects.create_user(
            username="agent",
            email="agent@example.com",
            password="agent123",
            tenant=tenant,
            role="agent",
        )

        practitioner = User.objects.create_user(
            username="doctor",
            email="doctor@example.com",
            password="doctor123",
            tenant=tenant,
            role="practitioner",
            first_name="Alex",
            last_name="Doctor",
        )

        # Second tenant (useful for verifying tenant isolation)
        other_tenant = Tenant.objects.create(name="Other Organisation")
        User.objects.create_user(
            username="otheradmin",
            email="otheradmin@example.com",
            password="other123",
            tenant=other_tenant,
            role="admin",
        )

        # Contacts
        contacts = []
        contacts.append(Contact.objects.create(tenant=tenant, created_by=admin, first_name="Emma", last_name="Stone", email="emma@example.com", phone="0700000001"))
        contacts.append(Contact.objects.create(tenant=tenant, created_by=admin, first_name="Noah", last_name="Jones", email="noah@example.com", phone="0700000002"))
        contacts.append(Contact.objects.create(tenant=tenant, created_by=admin, first_name="Olivia", last_name="Brown", email="olivia@example.com", phone="0700000003"))
        contacts.append(Contact.objects.create(tenant=tenant, created_by=admin, first_name="Liam", last_name="Wilson", email="liam@example.com", phone="0700000004"))

        # Deals
        Deal.objects.create(tenant=tenant, created_by=admin, name="Starter Package", contact=contacts[0], amount=199.00, stage="new")
        Deal.objects.create(tenant=tenant, created_by=admin, name="Monthly Retainer", contact=contacts[1], amount=999.00, stage="in_progress")
        Deal.objects.create(tenant=tenant, created_by=admin, name="Renewal", contact=contacts[2], amount=499.00, stage="won")

        # Patients
        patients = []
        patients.append(Patient.objects.create(tenant=tenant, created_by=admin, first_name="John", last_name="Smith", email="john.smith@example.com", phone="0711111111"))
        patients.append(Patient.objects.create(tenant=tenant, created_by=admin, first_name="Mia", last_name="Taylor", email="mia.taylor@example.com", phone="0722222222"))
        patients.append(Patient.objects.create(tenant=tenant, created_by=admin, first_name="Ethan", last_name="Moore", email="ethan.moore@example.com", phone="0733333333"))
        patients.append(Patient.objects.create(tenant=tenant, created_by=admin, first_name="Sophia", last_name="Hall", email="sophia.hall@example.com", phone="0744444444"))

        # Appointments
        now = timezone.now()
        Appointment.objects.create(tenant=tenant, created_by=admin, patient=patients[0], practitioner=practitioner, scheduled_at=now, reason="Checkup", status="scheduled")
        Appointment.objects.create(tenant=tenant, created_by=admin, patient=patients[1], practitioner=practitioner, scheduled_at=now + timezone.timedelta(days=1), reason="Follow-up", status="scheduled")
        Appointment.objects.create(tenant=tenant, created_by=admin, patient=patients[2], practitioner=None, scheduled_at=now + timezone.timedelta(days=2), reason="Consultation", status="scheduled")

        # Properties
        properties = []
        properties.append(Property.objects.create(tenant=tenant, created_by=admin, name="Flat A", address="10 High Street", city="London", price=350000, status="listed"))
        properties.append(Property.objects.create(tenant=tenant, created_by=admin, name="House B", address="22 Park Road", city="Manchester", price=420000, status="listed"))
        properties.append(Property.objects.create(tenant=tenant, created_by=admin, name="Studio C", address="5 River View", city="Leeds", price=180000, status="listed"))

        # Viewings (link to contacts)
        Viewing.objects.create(tenant=tenant, created_by=admin, property=properties[0], contact=contacts[0], scheduled_at=now + timezone.timedelta(days=3), notes="First viewing")
        Viewing.objects.create(tenant=tenant, created_by=admin, property=properties[1], contact=contacts[1], scheduled_at=now + timezone.timedelta(days=4), notes="Interested buyer")
        Viewing.objects.create(tenant=tenant, created_by=admin, property=properties[2], contact=contacts[2], scheduled_at=now + timezone.timedelta(days=5), notes="Budget check")

        self.stdout.write(self.style.SUCCESS("Demo data created."))
        self.stdout.write("\nTenant 1 (Demo Organisation) users:")
        self.stdout.write("  admin / admin123 (role: admin)")
        self.stdout.write("  manager / manager123 (role: manager)")
        self.stdout.write("  agent / agent123 (role: agent)")
        self.stdout.write("  doctor / doctor123 (role: practitioner)")
        self.stdout.write("\nTenant 2 (Other Organisation) user:")
        self.stdout.write("  otheradmin / other123 (role: admin)")