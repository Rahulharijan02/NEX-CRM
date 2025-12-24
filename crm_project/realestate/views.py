from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from rest_framework import permissions, viewsets

from accounts.permissions import RoleBasedWritePermission

from .models import Property, Viewing
from .serializers import PropertySerializer, ViewingSerializer


def _parse_datetime_local(value: str | None):
    """Parse <input type=datetime-local> values.

    Browser sends: YYYY-MM-DDTHH:MM
    """
    if not value:
        return None
    try:
        dt = datetime.strptime(value, '%Y-%m-%dT%H:%M')
        if timezone.is_naive(dt):
            dt = timezone.make_aware(dt)
        return dt
    except Exception:
        return None


class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedWritePermission]
    write_roles = {'admin', 'manager', 'agent'}

    search_fields = ['name', 'address', 'city']
    filterset_fields = ['status', 'city']
    ordering_fields = ['id', 'price', 'created_at']

    def get_queryset(self):
        return Property.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


class ViewingViewSet(viewsets.ModelViewSet):
    serializer_class = ViewingSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedWritePermission]
    write_roles = {'admin', 'manager', 'agent'}

    search_fields = ['property__name', 'contact__first_name', 'contact__last_name']
    filterset_fields = ['property']
    ordering_fields = ['id', 'scheduled_at', 'created_at']

    def get_queryset(self):
        return Viewing.objects.filter(tenant=self.request.user.tenant).select_related('property', 'contact')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


# -----------------------------
# HTML pages (simple forms)
# -----------------------------

@login_required
def property_list(request):
    properties = Property.objects.filter(tenant=request.user.tenant).order_by('id')
    return render(request, 'properties_list.html', {'properties': properties})


@login_required
@require_http_methods(["POST"])
def property_create(request):
    if request.user.role not in {'admin', 'manager', 'agent'}:
        return HttpResponse('Not allowed for your role.', status=403)

    name = request.POST.get('name', '').strip()
    address = request.POST.get('address', '').strip()
    city = request.POST.get('city', '').strip()
    status = request.POST.get('status', 'listed')
    price = request.POST.get('price', '').strip() or None
    description = request.POST.get('description', '').strip()

    if name and address:
        prop = Property.objects.create(
            tenant=request.user.tenant,
            created_by=request.user,
            name=name,
            address=address,
            city=city,
            status=status,
            price=price,
            description=description,
        )

        if request.headers.get('HX-Request'):
            return render(request, 'partials/property_row.html', {'property': prop})

    return redirect('realestate:properties')


@login_required
def viewing_list(request):
    viewings = Viewing.objects.filter(tenant=request.user.tenant).select_related('property', 'contact').order_by('id')
    properties = Property.objects.filter(tenant=request.user.tenant).order_by('id')
    # Contacts are in CRM app
    from crm.models import Contact  # local import keeps it simple
    contacts = Contact.objects.filter(tenant=request.user.tenant).order_by('id')

    return render(request, 'viewings_list.html', {
        'viewings': viewings,
        'properties': properties,
        'contacts': contacts,
    })


@login_required
@require_http_methods(["POST"])
def viewing_create(request):
    if request.user.role not in {'admin', 'manager', 'agent'}:
        return HttpResponse('Not allowed for your role.', status=403)

    property_id = request.POST.get('property', '')
    contact_id = request.POST.get('contact', '')
    scheduled_at_raw = request.POST.get('scheduled_at', '')
    notes = request.POST.get('notes', '').strip()

    prop = get_object_or_404(Property, pk=property_id, tenant=request.user.tenant)
    from crm.models import Contact  # local import keeps it simple
    contact = get_object_or_404(Contact, pk=contact_id, tenant=request.user.tenant)

    scheduled_at = _parse_datetime_local(scheduled_at_raw) or timezone.now()

    viewing = Viewing.objects.create(
        tenant=request.user.tenant,
        created_by=request.user,
        property=prop,
        contact=contact,
        scheduled_at=scheduled_at,
        notes=notes,
    )

    if request.headers.get('HX-Request'):
        return render(request, 'partials/viewing_row.html', {'viewing': viewing})

    return redirect('realestate:viewings')
