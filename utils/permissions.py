from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )