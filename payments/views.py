from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from students.models import Student
from attendance.views import _get_workdays_for_month
from attendance.models import Attendance
from .models import Payment
from .serializers import PaymentSerializer, PaymentListSerializer
from utils.permissions import IsSuperAdmin, IsAdminOrSuperAdmin


class PaymentViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Payment.objects.all()

    def get_permissions(self):
        if self.action == 'report':
            return [IsSuperAdmin()]
        return [IsAdminOrSuperAdmin()]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['student__full_name']
    ordering_fields = ['created_at', 'payment_date', 'month', 'year']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        payment_status = self.request.query_params.get('status')

        if student_id:
            try:
                queryset = queryset.filter(student_id=int(student_id))
            except ValueError:
                pass
        if month:
            try:
                queryset = queryset.filter(month=int(month))
            except ValueError:
                pass
        if year:
            try:
                queryset = queryset.filter(year=int(year))
            except ValueError:
                pass
        if payment_status:
            queryset = queryset.filter(status=payment_status)

        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return PaymentListSerializer
        return PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)

    def _duplicate_response(self):
        return Response(
            {
                'error_code': 'DUPLICATE_ENTRY',
                'detail': 'Payment for this student/month/year already exists.',
            },
            status=status.HTTP_409_CONFLICT,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            if 'non_field_errors' in serializer.errors:
                return self._duplicate_response()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return self._duplicate_response()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        ]
    )
    @action(detail=False, methods=['get'], url_path='calculate')
    def calculate(self, request):
        """Calculate payment amount for a student in a given month."""
        student_id = request.query_params.get('student_id')
        month = request.query_params.get('month')
        year = request.query_params.get('year')

        if not all([student_id, month, year]):
            return Response(
                {'detail': 'student_id, month, and year are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student = Student.objects.get(id=student_id)
            month = int(month)
            year = int(year)
        except (Student.DoesNotExist, ValueError):
            return Response(
                {'detail': 'Invalid student_id, month, or year.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        monthly_fee = student.monthly_fee
        workdays = _get_workdays_for_month(year, month)
        total_workdays = len(workdays)

        attendances = Attendance.objects.filter(
            student_id=student_id,
            date__year=year,
            date__month=month,
        )

        days_present = attendances.filter(status='present').count()
        days_absent = attendances.filter(status='absent').count()

        daily_rate = monthly_fee / total_workdays if total_workdays > 0 else 0
        calculated_amount = daily_rate * days_present

        existing_payment = Payment.objects.filter(
            student_id=student_id,
            month=month,
            year=year
        ).first()

        paid_amount = existing_payment.paid_amount if existing_payment else 0
        remaining = calculated_amount - paid_amount

        return Response({
            'student_id': student_id,
            'student_name': student.full_name,
            'month': month,
            'year': year,
            'monthly_fee': float(monthly_fee),
            'total_workdays': total_workdays,
            'days_present': days_present,
            'days_absent': days_absent,
            'daily_rate': float(daily_rate),
            'calculated_amount': float(calculated_amount),
            'paid_amount': float(paid_amount),
            'remaining': float(remaining),
            'status': existing_payment.status if existing_payment else 'unpaid'
        })

    @action(detail=False, methods=['get'], url_path='debtors')
    def debtors(self, request):
        """Return students with unpaid or partial payments."""
        unpaid_payments = Payment.objects.filter(
            status__in=['unpaid', 'partial', 'overdue']
        ).select_related('student').order_by('-created_at')

        data = []
        seen_students = set()

        for payment in unpaid_payments:
            if payment.student_id not in seen_students:
                seen_students.add(payment.student_id)
                data.append({
                    'student_id': payment.student_id,
                    'student_name': payment.student.full_name,
                    'month': payment.month,
                    'year': payment.year,
                    'calculated_amount': float(payment.calculated_amount),
                    'paid_amount': float(payment.paid_amount),
                    'remaining': float(payment.calculated_amount - payment.paid_amount),
                    'status': payment.status
                })

        return Response(data)

    @swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, enum=['paid', 'partial', 'unpaid', 'overdue']),
    ]
)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    @action(detail=False, methods=['get'], url_path='report')
    def report(self, request):
        """Get monthly payment report."""
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
        except ValueError:
            return Response(
                {'detail': 'month and year must be integers.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payments = Payment.objects.filter(month=month, year=year)

        total_students = payments.values('student_id').distinct().count()
        total_calculated = sum(p.calculated_amount for p in payments)
        total_paid = sum(p.paid_amount for p in payments)
        total_remaining = total_calculated - total_paid

        payment_list = PaymentListSerializer(payments, many=True).data

        return Response({
            'month': month,
            'year': year,
            'total_students': total_students,
            'total_calculated': float(total_calculated),
            'total_paid': float(total_paid),
            'total_remaining': float(total_remaining),
            'payments': payment_list
        })
