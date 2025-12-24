"""
Custom permission classes for role‑based access control.

These classes can be applied to DRF viewsets to restrict access based on
the user's `role` field. While the default viewsets in this project
simply require authentication, these permissions provide a foundation
for more granular control in future iterations.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrManager(BasePermission):
    """Allows access only to admins or managers."""

    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.role in {'admin', 'manager'}


class IsPractitioner(BasePermission):
    """Allows access only to practitioners."""

    def has_permission(self, request, view) -> bool:
        return request.user.is_authenticated and request.user.role == 'practitioner'


class IsAdminOrReadOnly(BasePermission):
    """Allows full access to admins/managers and read‑only access to others."""

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role in {'admin', 'manager'}


class RoleBasedWritePermission(BasePermission):
    """Read for any authenticated user, write only for allowed roles.

    ViewSets may define a class attribute `write_roles` (set of strings)
    to override the default.
    """

    default_write_roles = {'admin', 'manager'}

    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        allowed = getattr(view, 'write_roles', self.default_write_roles)
        return request.user.is_authenticated and request.user.role in allowed