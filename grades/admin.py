from django.contrib import admin
from .models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'subject', 'teacher', 'score', 'date']
    list_filter = ['subject', 'teacher', 'date']
    search_fields = ['student__full_name', 'subject__title', 'teacher__name']
    readonly_fields = ['id']
