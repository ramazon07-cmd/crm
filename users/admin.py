from django.contrib import admin
from .models import User

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