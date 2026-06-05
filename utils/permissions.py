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


class IsSuperAdmin(BasePermission):
    """Only SUPER_ADMIN role."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'SUPER_ADMIN'
        )


class IsAdminOrSuperAdmin(BasePermission):
    """ADMIN or SUPER_ADMIN role."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('ADMIN', 'SUPER_ADMIN')
        )


class IsTeacherOrAbove(BasePermission):
    """Any authenticated user with a valid role."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('TEACHER', 'ADMIN', 'SUPER_ADMIN')
        )


class IsOwnerTeacher(BasePermission):
    """Teacher can only access their own groups."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'SUPER_ADMIN':
            return True
        if request.user.role == 'ADMIN':
            return True
        # Teacher: check if group belongs to them
        if hasattr(obj, 'teacher'):
            return obj.teacher.user == request.user
        return False
