from django.contrib import admin
from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'age']
    list_filter = ['age']
    search_fields = ['full_name']
    readonly_fields = ['id']