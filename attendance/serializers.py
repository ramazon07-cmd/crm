from django.utils import timezone
from rest_framework import serializers

from .models import Attendance, Holiday

VALID_ATTENDANCE_STATUSES = {'present', 'absent', 'excused'}


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = [
            'id', 'student', 'group', 'date', 'status', 'marked_by', 'note',
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
            'id', 'student', 'group', 'date', 'status', 'note', 'created_at',
        ]


class BulkAttendanceRecordSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=[s[0] for s in Attendance.STATUS_CHOICES])
    note = serializers.CharField(max_length=200, required=False, default='')


class BulkAttendanceSerializer(serializers.Serializer):
    group_id = serializers.IntegerField()
    date = serializers.DateField()
    records = BulkAttendanceRecordSerializer(many=True)

    def validate_date(self, value):
        if value > timezone.localdate():
            raise serializers.ValidationError('Date cannot be in the future.')
        return value

    def validate_records(self, value):
        if not value:
            raise serializers.ValidationError('At least one record is required.')
        return value

    def validate_group_id(self, value):
        from groups.models import Group
        try:
            Group.objects.get(id=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError('Group not found.')
        return value

    def validate(self, data):
        # Validate student_ids exist and belong to the group
        from students.models import Student
        student_ids = [r['student_id'] for r in data['records']]
        students = Student.objects.filter(id__in=student_ids, group_id=data['group_id'])
        found_ids = {s.id for s in students}
        missing = set(student_ids) - found_ids
        if missing:
            raise serializers.ValidationError(
                f'Students {missing} not found in group {data["group_id"]}.'
            )
        return data


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
