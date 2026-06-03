from django.contrib import admin

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = [
        'full_name',
        'phone',
        'subject',
        'salary_type',
        'status',
        'created_at',
    ]
    search_fields = ['full_name', 'phone', 'subject']
    list_filter = ['status', 'salary_type', 'created_at']
