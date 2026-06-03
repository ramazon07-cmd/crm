from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'status', 'monthly_fee', 'created_at']
    search_fields = ['full_name', 'phone']
    list_filter = ['status', 'created_at']
