from django.contrib import admin
from .models import User, AuditLog

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email',
        'username',
        'first_name',
        'last_name',
        'created_at'
    ]

    search_fields = ['email', 'username']

    list_filter = [
        'created_at',
        'is_active',
        'is_verified'
    ]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'timestamp']
    search_fields = ['user__email', 'model_name', 'object_repr']
    list_filter = ['action', 'model_name', 'timestamp']
    readonly_fields = ['user', 'action', 'model_name', 'object_id', 'object_repr', 'changes', 'ip_address', 'timestamp']