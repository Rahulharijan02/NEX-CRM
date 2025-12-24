from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from rest_framework import permissions, viewsets

from accounts.models import User
from accounts.permissions import RoleBasedWritePermission

from .models import Appointment, Patient
# -----------------------------
# Small helpers (beginner-friendly)
# -----------------------------

def _parse_date(value: str | None):
    """Parse <input type=date> values (YYYY-MM-DD)."""
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except Exception:
        return None


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

from .serializers import AppointmentSerializer, PatientSerializer


# -----------------------------
# API (DRF)
# -----------------------------

class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedWritePermission]
    write_roles = {'admin', 'manager', 'practitioner'}

    search_fields = ['first_name', 'last_name', 'email', 'phone']
    filterset_fields = ['email', 'phone']
    ordering_fields = ['id', 'last_name', 'created_at']

    def get_queryset(self):
        return Patient.objects.filter(tenant=self.request.user.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedWritePermission]
    write_roles = {'admin', 'manager', 'practitioner'}

    search_fields = ['patient__first_name', 'patient__last_name', 'reason']
    filterset_fields = ['status', 'practitioner']
    ordering_fields = ['id', 'scheduled_at', 'created_at']

    def get_queryset(self):
        return Appointment.objects.filter(tenant=self.request.user.tenant).select_related('patient', 'practitioner')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant, created_by=self.request.user)


# -----------------------------
# HTML pages (simple forms)
# -----------------------------

@login_required
def patient_list(request):
    patients = Patient.objects.filter(tenant=request.user.tenant).order_by('id')
    return render(request, 'patients_list.html', {'patients': patients})


@login_required
@require_http_methods(["POST"])
def patient_create(request):
    if request.user.role not in {'admin', 'manager', 'practitioner'}:
        return HttpResponse('Not allowed for your role.', status=403)

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    dob_raw = request.POST.get('date_of_birth', '').strip()
    dob = _parse_date(dob_raw)

    if first_name and last_name:
        patient = Patient.objects.create(
            tenant=request.user.tenant,
            created_by=request.user,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            date_of_birth=dob,
        )
        if request.headers.get('HX-Request'):
            return render(request, 'partials/patient_row.html', {'patient': patient})

    return redirect('clinic:patients')


@login_required
def appointment_list(request):
    appointments = Appointment.objects.filter(tenant=request.user.tenant).select_related('patient', 'practitioner').order_by('id')
    patients = Patient.objects.filter(tenant=request.user.tenant).order_by('id')
    practitioners = User.objects.filter(tenant=request.user.tenant, role='practitioner').order_by('id')

    return render(request, 'appointments_list.html', {
        'appointments': appointments,
        'patients': patients,
        'practitioners': practitioners,
    })


@login_required
@require_http_methods(["POST"])
def appointment_create(request):
    if request.user.role not in {'admin', 'manager', 'practitioner'}:
        return HttpResponse('Not allowed for your role.', status=403)

    patient_id = request.POST.get('patient', '')
    practitioner_id = request.POST.get('practitioner', '') or None
    scheduled_at_raw = request.POST.get('scheduled_at', '')
    scheduled_at = _parse_datetime_local(scheduled_at_raw) or timezone.now()
    reason = request.POST.get('reason', '').strip()
    status = request.POST.get('status', 'scheduled')

    patient = get_object_or_404(Patient, pk=patient_id, tenant=request.user.tenant)
    practitioner = None
    if practitioner_id:
        practitioner = get_object_or_404(User, pk=practitioner_id, tenant=request.user.tenant)

    appointment = Appointment.objects.create(
        tenant=request.user.tenant,
        created_by=request.user,
        patient=patient,
        practitioner=practitioner,
        scheduled_at=scheduled_at,
        reason=reason,
        status=status,
    )

    if request.headers.get('HX-Request'):
        return render(request, 'partials/appointment_row.html', {'appointment': appointment})

    return redirect('clinic:appointments')
