from django.utils import timezone
from rest_framework import serializers

from .models import Attendance, Holiday

VALID_ATTENDANCE_STATUSES = {'present', 'absent', 'excused'}


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'group',
            'date',
            'status',
            'marked_by',
            'note',
            'created_at',
        ]
        read_only_fields = ['id', 'marked_by', 'created_at']

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError('Date cannot be in the future.')
        return value

    def validate_status(self, value):
        if value not in VALID_ATTENDANCE_STATUSES:
            raise serializers.ValidationError(
                'Status must be present, absent, or excused.'
            )
        return value

    def validate_note(self, value):
        if value is not None and len(value) > 200:
            raise serializers.ValidationError(
                'Note must be at most 200 characters.'
            )
        return value


class AttendanceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'group',
            'date',
            'status',
            'note',
            'created_at',
        ]


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = ['id', 'date', 'name', 'type', 'recurring']
        read_only_fields = ['id']

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
        return value
