from rest_framework import serializers

from teachers.models import Teacher

from .models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'teacher',
            'schedule',
            'start_time',
            'capacity',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError(
                'Name must be at least 2 characters.'
            )
        if len(value) > 100:
            raise serializers.ValidationError(
                'Name must be at most 100 characters.'
            )
        queryset = Group.objects.filter(name=value, deleted_at__isnull=True)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('DUPLICATE_NAME')
        return value

    def validate_teacher(self, value):
        if value is None:
            return value
        if value.deleted_at is not None:
            raise serializers.ValidationError(
                'Selected teacher is not available.'
            )
        if not Teacher.objects.filter(
            pk=value.pk, deleted_at__isnull=True
        ).exists():
            raise serializers.ValidationError('Teacher does not exist.')
        return value

    def validate_schedule(self, value):
        if value is None:
            return value
        if not isinstance(value, list):
            raise serializers.ValidationError('Schedule must be a list.')
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                'Schedule must not contain duplicate days.'
            )
        for day in value:
            if not isinstance(day, int) or day < 1 or day > 7:
                raise serializers.ValidationError(
                    'Schedule days must be integers between 1 and 7.'
                )
        return value

    def validate_capacity(self, value):
        if value is not None and value < 1:
            raise serializers.ValidationError(
                'Capacity must be at least 1 when provided.'
            )
        return value


class TeacherNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'full_name']


class GroupListSerializer(serializers.ModelSerializer):
    teacher = TeacherNestedSerializer(read_only=True)

    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'teacher',
            'start_time',
            'capacity',
            'status',
            'created_at',
        ]
