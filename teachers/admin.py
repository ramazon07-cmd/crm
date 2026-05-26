from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'experience']
    list_filter = ['experience']
    search_fields = ['name']
    readonly_fields = ['id']