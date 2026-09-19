from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedAndAdminWrite(BasePermission):
    """Regular users can read. Only staff users can change data."""

    message = "Only admin users can create, update, or delete records."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_staff or request.user.is_superuser

