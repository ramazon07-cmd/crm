from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['student', 'month', 'year', 'calculated_amount', 'paid_amount', 'status', 'payment_date']
    search_fields = ['student__full_name']
    list_filter = ['status', 'payment_method', 'month', 'year']
