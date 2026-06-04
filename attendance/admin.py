from django.contrib import admin

from .models import Attendance, Holiday


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'group', 'date', 'status', 'marked_by', 'created_at']
    search_fields = ['student__full_name', 'group__name']
    list_filter = ['status', 'date']


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'type', 'recurring']
    search_fields = ['name']
    list_filter = ['type', 'recurring']
