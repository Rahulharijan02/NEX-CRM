

from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from crm.models import Contact, Deal
from clinic.models import Patient, Appointment
from realestate.models import Property, Viewing


def home(request: HttpRequest) -> HttpResponse:
    """Redirect to a friendly starting page.

    - Authenticated users go to the Contacts list.
    - Anonymous users go to the login page.
    """

    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """A simple dashboard showing key counts and quick links.

    We keep this intentionally basic for first-year readability.
    """

    tenant = request.user.tenant
    role = request.user.role

    # Counts are always tenant-scoped.
    counts = {
        'contacts': Contact.objects.filter(tenant=tenant).count(),
        'deals': Deal.objects.filter(tenant=tenant).count(),
        'patients': Patient.objects.filter(tenant=tenant).count(),
        'appointments': Appointment.objects.filter(tenant=tenant).count(),
        'properties': Property.objects.filter(tenant=tenant).count(),
        'viewings': Viewing.objects.filter(tenant=tenant).count(),
    }

    # What modules should be shown for this role?
    show_sales = role in {'admin', 'manager', 'agent'}
    show_clinic = role in {'admin', 'manager', 'practitioner'}
    show_realestate = role in {'admin', 'manager', 'agent'}

    return render(
        request,
        'dashboard.html',
        {
            'counts': counts,
            'show_sales': show_sales,
            'show_clinic': show_clinic,
            'show_realestate': show_realestate,
        },
    )
