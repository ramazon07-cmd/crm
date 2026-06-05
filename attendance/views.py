import calendar
from datetime import date

from django.db import IntegrityError
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from students.models import Student
from .models import Attendance, Holiday
from .serializers import (
    AttendanceListSerializer,
    AttendanceSerializer,
    BulkAttendanceSerializer,
    HolidaySerializer,
)


class AttendanceViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Attendance.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['student__full_name', 'group__name']
    ordering_fields = ['date', 'created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        group_id = self.request.query_params.get('group_id')
        date = self.request.query_params.get('date')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if group_id:
            queryset = queryset.filter(group_id=group_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return AttendanceListSerializer
        return AttendanceSerializer

    def perform_create(self, serializer):
        serializer.save(marked_by=self.request.user)

    def _duplicate_entry_response(self):
        return Response(
            {
                'error_code': 'DUPLICATE_ENTRY',
                'detail': (
                    'Attendance for this student on this date already exists.'
                ),
            },
            status=status.HTTP_409_CONFLICT,
        )

    def _check_restricted_date(self, date_value):
        """Check if date is a weekend or holiday. Returns Response or None."""
        if date_value.weekday() in (5, 6):
            return Response(
                {
                    'error_code': 'WEEKEND',
                    'detail': 'Attendance cannot be marked on weekends.',
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        recurring_match = Holiday.objects.filter(
            recurring=True,
            date__month=date_value.month,
            date__day=date_value.day,
        ).exists()
        exact_match = Holiday.objects.filter(
            recurring=False,
            date=date_value,
        ).exists()

        if recurring_match or exact_match:
            return Response(
                {
                    'error_code': 'HOLIDAY',
                    'detail': 'Attendance cannot be marked on a holiday.',
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return None

    def create(self, request, *args, **kwargs):
        date_str = request.data.get('date')
        if date_str:
            try:
                from datetime import date
                parsed_date = date.fromisoformat(date_str)
                # 2. Weekend/holiday tekshiruvi — is_valid() DAN OLDIN
                restricted = self._check_restricted_date(parsed_date)
                if restricted:
                    return restricted
            except ValueError:
                pass  # serializer o'zi xato beradi

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            if 'non_field_errors' in serializer.errors:
                return self._duplicate_entry_response()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return self._duplicate_entry_response()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            if 'non_field_errors' in serializer.errors:
                return self._duplicate_entry_response()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        date_value = serializer.validated_data.get('date', instance.date)
        if date_value:
            restricted = self._check_restricted_date(date_value)
            if restricted:
                return restricted

        try:
            serializer.save()
        except IntegrityError:
            return self._duplicate_entry_response()
        return Response(serializer.data)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('group_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # ---- Bulk attendance endpoint ----

    @action(detail=False, methods=['post'], url_path='bulk')
    @swagger_auto_schema(
        request_body=BulkAttendanceSerializer,
        operation_description='Mark attendance for multiple students in a group at once.',
        responses={
            200: 'Bulk attendance created/updated',
            400: 'Validation error',
            422: 'Weekend or holiday',
        },
    )
    def bulk(self, request):
        """POST /api/attendance/bulk/ — bulk mark attendance for a group."""
        serializer = BulkAttendanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group_id = serializer.validated_data['group_id']
        date_value = serializer.validated_data['date']
        records = serializer.validated_data['records']

        # Future date check
        if date_value > timezone.localdate():
            return Response(
                {'detail': 'Date cannot be in the future.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Weekend / holiday check
        restricted = self._check_restricted_date(date_value)
        if restricted:
            return restricted

        created_count = 0
        updated_count = 0

        for record in records:
            student_id = record['student_id']
            record_status = record['status']
            note = record.get('note', '')

            _, was_created = Attendance.objects.update_or_create(
                student_id=student_id,
                date=date_value,
                defaults={
                    'group_id': group_id,
                    'status': record_status,
                    'note': note,
                    'marked_by': request.user,
                },
            )
            if was_created:
                created_count += 1
            else:
                updated_count += 1

        return Response({
            'success': True,
            'date': str(date_value),
            'group_id': group_id,
            'total': len(records),
            'created': created_count,
            'updated': updated_count,
        })

    # ---- Attendance summary endpoint ----

    @action(detail=False, methods=['get'], url_path='summary')
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
            ),
            openapi.Parameter(
                'month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
            ),
        ],
        operation_description='Get attendance summary for a student in a given month.',
        responses={200: 'Attendance summary'},
    )
    def summary(self, request):
        """GET /api/attendance/summary/?student_id=&month=&year="""
        student_id = request.query_params.get('student_id')
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not all([student_id, month, year]):
            return Response(
                {'detail': 'student_id, month, and year are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student_id = int(student_id)
            month = int(month)
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'student_id, month, and year must be integers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response(
                {'detail': 'Student not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        workdays = _get_workdays_for_month(year, month)
        total_workdays = len(workdays)

        attendances = Attendance.objects.filter(
            student_id=student_id,
            date__year=year,
            date__month=month,
        )

        days_present = attendances.filter(status='present').count()
        days_absent = attendances.filter(status='absent').count()
        days_excused = attendances.filter(status='excused').count()

        return Response({
            'student_id': student_id,
            'student_name': student.full_name,
            'month': month,
            'year': year,
            'total_workdays': total_workdays,
            'days_present': days_present,
            'days_absent': days_absent,
            'days_excused': days_excused,
        })


# ---- Helper function for workdays ----

def _get_workdays_for_month(year, month):
    """Return list of workday date strings for a given month/year."""
    _, num_days = calendar.monthrange(year, month)
    # Fetch all holidays once to avoid N+1
    all_holidays = set(
        Holiday.objects.filter(
            Q(recurring=True, date__month=month)
            | Q(recurring=False, date__year=year, date__month=month)
        ).values_list('date', flat=True)
    )
    workdays = []
    for day in range(1, num_days + 1):
        d = date(year, month, day)
        if d.weekday() in (5, 6):
            continue
        if d in all_holidays:
            continue
        workdays.append(str(d))
    return workdays


class WorkdaysView(APIView):
    """GET /api/workdays/?month=&year= — calculate workdays for a month."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
            ),
            openapi.Parameter(
                'year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
            ),
        ],
        operation_description='Get total workdays (excluding weekends and holidays) for a month.',
        responses={200: 'Workday list'},
    )
    def get(self, request):
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not all([month, year]):
            return Response(
                {'detail': 'month and year are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            month = int(month)
            year = int(year)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'month and year must be integers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if month < 1 or month > 12:
            return Response(
                {'detail': 'month must be between 1 and 12.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workdays = _get_workdays_for_month(year, month)

        return Response({
            'month': month,
            'year': year,
            'total_workdays': len(workdays),
            'workdays': workdays,
        })


class HolidayViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    ordering_fields = ['date']
