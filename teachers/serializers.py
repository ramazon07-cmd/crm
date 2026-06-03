import re

from rest_framework import serializers

from .models import Teacher

PHONE_PATTERN = re.compile(r'^\+998\d{9}$')
SALARY_TYPES = ('fixed', 'percent')


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id',
            'full_name',
            'phone',
            'email',
            'subject',
            'salary_type',
            'salary_value',
            'status',
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
        queryset = Teacher.objects.filter(phone=value, deleted_at__isnull=True)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('DUPLICATE_PHONE')
        return value

    def validate_email(self, value):
        if not value:
            return value
        queryset = Teacher.objects.filter(email=value, deleted_at__isnull=True)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('DUPLICATE_EMAIL')
        return value

    def validate_salary_type(self, value):
        if value not in SALARY_TYPES:
            raise serializers.ValidationError(
                'Salary type must be "fixed" or "percent".'
            )
        return value

    def validate(self, attrs):
        salary_type = attrs.get(
            'salary_type',
            getattr(self.instance, 'salary_type', None) if self.instance else None,
        )
        salary_value = attrs.get(
            'salary_value',
            getattr(self.instance, 'salary_value', None) if self.instance else None,
        )

        if salary_type is None or salary_value is None:
            return attrs

        if salary_type == 'fixed' and salary_value < 0:
            raise serializers.ValidationError({
                'salary_value': (
                    'For fixed salary, value must be greater than or equal to 0.'
                ),
            })

        if salary_type == 'percent' and (salary_value < 0 or salary_value > 100):
            raise serializers.ValidationError({
                'salary_value': (
                    'For percent salary, value must be between 0 and 100.'
                ),
            })

        return attrs


class TeacherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'id',
            'full_name',
            'phone',
            'subject',
            'salary_type',
            'status',
            'created_at',
        ]
