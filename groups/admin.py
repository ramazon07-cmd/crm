from django.contrib import admin

from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'start_time', 'capacity', 'status', 'created_at']
    search_fields = ['name', 'teacher__full_name']
    list_filter = ['status', 'created_at']
