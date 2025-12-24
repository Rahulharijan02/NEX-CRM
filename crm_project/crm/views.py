from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from rest_framework import permissions, viewsets

from accounts.permissions import RoleBasedWritePermission

from .models import Activity, Contact, Deal
from .serializers import ActivitySerializer, ContactSerializer, DealSerializer


def _parse_date(value: str | None):
    """Parse <input type=date> values (YYYY-MM-DD)."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except Exception:
        return None


# -----------------------------
# API (DRF)
# -----------------------------

class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedWritePermission]
    write_roles = {'admin', 'manager', 'agent'}

    search_fields = ['first_name', 'last_name', 'email', 'phone']
    filterset_fields = ['email', 'phone']
    ordering_fields = ['id', 'first_name', 'last_name', 'created_at']

    def get_queryset(self):
        return Contact.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


class DealViewSet(viewsets.ModelViewSet):
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedWritePermission]
    write_roles = {'admin', 'manager', 'agent'}

    search_fields = ['name', 'stage', 'contact__first_name', 'contact__last_name']
    filterset_fields = ['stage', 'close_date']
    ordering_fields = ['id', 'amount', 'close_date', 'created_at']

    def get_queryset(self):
        return Deal.objects.filter(tenant=self.request.user.tenant).select_related('contact')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


class ActivityViewSet(viewsets.ModelViewSet):
    serializer_class = ActivitySerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedWritePermission]
    # Activities are allowed for all roles
    write_roles = {'admin', 'manager', 'agent', 'practitioner'}

    search_fields = ['title', 'type']
    filterset_fields = ['type', 'completed']
    ordering_fields = ['id', 'due_date', 'completed', 'created_at']

    def get_queryset(self):
        return Activity.objects.filter(tenant=self.request.user.tenant).select_related('contact', 'deal')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


# -----------------------------
# HTML pages (simple forms)
# -----------------------------

@login_required
def contact_list(request):
    contacts = Contact.objects.filter(tenant=request.user.tenant).order_by('id')
    return render(request, 'contacts_list.html', {'contacts': contacts})


@login_required
@require_http_methods(["POST"])
def contact_create(request):
    if request.user.role not in {'admin', 'manager', 'agent'}:
        return HttpResponse('Not allowed for your role.', status=403)

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()

    if first_name and last_name:
        contact = Contact.objects.create(
            tenant=request.user.tenant,
            created_by=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
        )
        if request.headers.get('HX-Request'):
            return render(request, 'partials/contact_row.html', {'contact': contact})

    return redirect('crm:contacts')


@login_required
def deal_list(request):
    deals = Deal.objects.filter(tenant=request.user.tenant).select_related('contact').order_by('id')
    contacts = Contact.objects.filter(tenant=request.user.tenant).order_by('id')
    return render(request, 'deals_list.html', {'deals': deals, 'contacts': contacts})


@login_required
@require_http_methods(["POST"])
def deal_create(request):
    if request.user.role not in {'admin', 'manager', 'agent'}:
        return HttpResponse('Not allowed for your role.', status=403)

    name = request.POST.get('name', '').strip()
    contact_id = request.POST.get('contact', '')
    amount = request.POST.get('amount', '').strip() or '0'
    stage = request.POST.get('stage', 'new')
    description = request.POST.get('description', '').strip()
    close_date_raw = request.POST.get('close_date', '').strip()
    close_date = _parse_date(close_date_raw)

    contact = get_object_or_404(Contact, pk=contact_id, tenant=request.user.tenant)
    deal = Deal.objects.create(
        tenant=request.user.tenant,
        created_by=request.user,
        name=name or f"Deal for {contact.first_name}",
        contact=contact,
        amount=amount,
        stage=stage,
        description=description,
        close_date=close_date,
    )

    if request.headers.get('HX-Request'):
        return render(request, 'partials/deal_row.html', {'deal': deal})

    return redirect('crm:deals')
