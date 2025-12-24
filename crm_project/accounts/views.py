"""Accounts views (login/register + user API)."""

from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from rest_framework import permissions, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from tenants.models import Tenant
from .serializers import UserSerializer


class IsTenantAdmin(permissions.BasePermission):
    """Only admin/manager can access."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in {'admin', 'manager'}


class UserViewSet(viewsets.ModelViewSet):
    """List users in the same tenant."""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantAdmin]

    def get_queryset(self):
        User = get_user_model()
        user = self.request.user
        return User.objects.filter(tenant=user.tenant)


class AuthView(TokenObtainPairView):
    """JWT login endpoint."""
    pass


@require_http_methods(["GET", "POST"])
def register(request):
    """Simple register page: create tenant + admin user."""

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        email = (request.POST.get("email") or "").strip()
        password = request.POST.get("password") or ""
        password2 = request.POST.get("password2") or ""

        errors = []
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")
        if password and len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != password2:
            errors.append("Passwords do not match.")

        UserModel = get_user_model()
        if username and UserModel.objects.filter(username=username).exists():
            errors.append("This username is already taken.")

        if not errors:
            # Create a tenant for this new user and make them admin of it.
            tenant = Tenant.objects.create(name=f"{username}'s Organisation")

            user = UserModel.objects.create_user(
                username=username,
                email=email,
                password=password,
                tenant=tenant,
                role="admin",
            )
            login(request, user)
            return redirect("crm:contacts")

        # If there are validation errors re‑render the form with messages.
        return render(request, "register.html", {"errors": errors})

    # GET request: show a blank form.
    return render(request, "register.html")
