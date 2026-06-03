import re

from rest_framework import serializers

from .models import Student

PHONE_PATTERN = re.compile(r'^\+998\d{9}$')


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'full_name',
            'phone',
            'group',
            'monthly_fee',
            'start_date',
            'status',
            'notes',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError(
                'Full name must be at least 3 characters.'
            )
        if len(value) > 150:
            raise serializers.ValidationError(
                'Full name must be at most 150 characters.'
            )
        return value

    def validate_phone(self, value):
        if not PHONE_PATTERN.match(value):
            raise serializers.ValidationError(
                'Phone must match format +998XXXXXXXXX.'
            )
        queryset = Student.objects.filter(phone=value, deleted_at__isnull=True)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('DUPLICATE_PHONE')  # ← unique kod
        return value

    def validate_monthly_fee(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'Monthly fee must be greater than or equal to 0.'
            )
        return value

    def validate_notes(self, value):
        if value is not None and len(value) > 1000:
            raise serializers.ValidationError(
                'Notes must be at most 1000 characters.'
            )
        return value


class StudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id',
            'full_name',
            'phone',
            'group',
            'monthly_fee',
            'start_date',
            'status',
            'created_at',
        ]
