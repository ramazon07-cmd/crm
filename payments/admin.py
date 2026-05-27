from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'amount', 'month', 'status', 'paid_at']
    list_filter = ['status', 'month']
    search_fields = ['student__full_name']
    readonly_fields = ['id']
