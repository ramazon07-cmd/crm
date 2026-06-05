from rest_framework import serializers
from django.utils import timezone
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'month', 'year', 'calculated_amount', 'paid_amount',
            'discount', 'payment_date', 'payment_method', 'status', 'received_by', 'note', 'created_at'
        ]
        read_only_fields = ['id', 'calculated_amount', 'received_by', 'created_at']

    def validate_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError("Month must be between 1 and 12.")
        return value

    def validate_year(self, value):
        if value < 2000 or value > 2100:
            raise serializers.ValidationError("Year must be between 2000 and 2100.")
        return value

    def validate_paid_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Paid amount must be >= 0.")
        return value

    def validate_discount(self, value):
        if value < 0:
            raise serializers.ValidationError("Discount must be >= 0.")
        return value

    def validate_payment_date(self, value):
        if value > timezone.now().date():
            raise serializers.ValidationError("Payment date cannot be in the future.")
        return value

    def validate(self, data):
        paid = data.get('paid_amount', 0)
        calculated = data.get('calculated_amount', 0)
        discount = data.get('discount', 0)

        # Determine status based on paid vs calculated-discount
        if paid >= (calculated - discount):
            data['status'] = 'paid'
        elif paid > 0:
            data['status'] = 'partial'
        else:
            data['status'] = 'unpaid'

        return data

    def create(self, validated_data):
        return Payment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'month', 'year', 'calculated_amount',
            'paid_amount', 'status', 'payment_date', 'created_at'
        ]
