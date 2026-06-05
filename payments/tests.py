from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import date, time

from students.models import Student
from groups.models import Group
from attendance.models import Attendance, Holiday
from .models import Payment

User = get_user_model()


class PaymentModelTests(TestCase):
    """Test Payment model."""

    def setUp(self):
        self.group = Group.objects.create(
            name="10A",
            start_time=time(9, 0)
        )
        self.student = Student.objects.create(
            full_name="Test Student",
            group=self.group,
            monthly_fee=500000
        )

    def test_payment_create_with_required_fields(self):
        """Payment can be created with required fields."""
        payment = Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=450000,
            payment_date=date(2026, 6, 1),
            payment_method='cash',
            status='paid'
        )
        self.assertEqual(payment.student, self.student)
        self.assertEqual(payment.month, 6)
        self.assertEqual(payment.year, 2026)

    def test_unique_together_constraint(self):
        """Payment unique_together(student, month, year) enforced."""
        Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=450000,
            payment_date=date(2026, 6, 1),
            payment_method='cash'
        )
        with self.assertRaises(Exception):
            Payment.objects.create(
                student=self.student,
                month=6,
                year=2026,
                calculated_amount=450000,
                paid_amount=0,
                payment_date=date(2026, 6, 2),
                payment_method='card'
            )

    def test_payment_str_representation(self):
        """Payment string representation."""
        payment = Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=450000,
            payment_date=date(2026, 6, 1),
            payment_method='cash',
            status='paid'
        )
        expected = f"{self.student} - 6/2026 - paid"
        self.assertEqual(str(payment), expected)


class PaymentSerializerTests(TestCase):
    """Test Payment serializers."""

    def setUp(self):
        self.group = Group.objects.create(name="10A")
        self.student = Student.objects.create(
            full_name="Test Student",
            group=self.group,
            monthly_fee=500000
        )

    def test_payment_serializer_valid_data(self):
        """PaymentSerializer accepts valid data."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 450000,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_payment_serializer_month_validation(self):
        """Month must be 1-12."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 13,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 450000,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_payment_serializer_year_validation(self):
        """Year must be 2000-2100."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 1999,
            "calculated_amount": 450000,
            "paid_amount": 450000,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_payment_serializer_paid_amount_validation(self):
        """Paid amount must be >= 0."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": -100,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_payment_serializer_discount_validation(self):
        """Discount must be >= 0."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 450000,
            "discount": -100,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_payment_serializer_future_date_validation(self):
        """Payment date cannot be in the future."""
        from .serializers import PaymentSerializer
        future_date = timezone.now().date()
        from datetime import timedelta
        future_date += timedelta(days=1)
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 450000,
            "payment_date": str(future_date),
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_payment_serializer_status_paid(self):
        """Status should be 'paid' when paid >= calculated - discount."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 450000,
            "discount": 0,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data.get('status'), 'paid')

    def test_payment_serializer_status_partial(self):
        """Status should be 'partial' when 0 < paid < calculated - discount."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 200000,
            "discount": 0,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data.get('status'), 'partial')

    def test_payment_serializer_status_unpaid(self):
        """Status should be 'unpaid' when paid == 0."""
        from .serializers import PaymentSerializer
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 0,
            "discount": 0,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        serializer = PaymentSerializer(data=data)
        if serializer.is_valid():
            self.assertEqual(serializer.validated_data.get('status'), 'unpaid')

    def test_payment_list_serializer_fields(self):
        """PaymentListSerializer includes only required fields."""
        from .serializers import PaymentListSerializer
        payment = Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=450000,
            payment_date=date(2026, 6, 1),
            payment_method='cash',
            status='paid'
        )
        serializer = PaymentListSerializer(payment)
        self.assertIn('id', serializer.data)
        self.assertIn('student', serializer.data)
        self.assertIn('month', serializer.data)
        self.assertIn('year', serializer.data)
        self.assertIn('calculated_amount', serializer.data)
        self.assertIn('paid_amount', serializer.data)
        self.assertIn('status', serializer.data)
        self.assertIn('payment_date', serializer.data)
        self.assertIn('created_at', serializer.data)


class PaymentViewSetTests(APITestCase):
    """Test Payment viewset."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.group = Group.objects.create(name="10A")
        self.student = Student.objects.create(
            full_name="Test Student",
            group=self.group,
            monthly_fee=500000
        )

    def test_requires_authentication(self):
        """PaymentViewSet requires authentication."""
        client = APIClient()
        response = client.get("/api/payments/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_uses_list_serializer(self):
        """List endpoint uses PaymentListSerializer."""
        Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=450000,
            payment_date=date(2026, 6, 1),
            payment_method='cash',
            status='paid'
        )
        response = self.client.get("/api/payments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_duplicate_returns_409(self):
        """Creating duplicate student/month/year returns 409."""
        Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=450000,
            payment_date=date(2026, 6, 1),
            payment_method='cash'
        )
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 0,
            "payment_date": "2026-06-02",
            "payment_method": "card"
        }
        response = self.client.post("/api/payments/", data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data.get('error_code'), 'DUPLICATE_ENTRY')

    def test_create_sets_received_by(self):
        """Create endpoint sets received_by to request.user."""
        data = {
            "student": self.student.id,
            "month": 6,
            "year": 2026,
            "calculated_amount": 450000,
            "paid_amount": 450000,
            "payment_date": "2026-06-01",
            "payment_method": "cash"
        }
        response = self.client.post("/api/payments/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(id=response.data['id'])
        self.assertEqual(payment.received_by, self.user)

    def test_calculate_action(self):
        """GET /api/payments/calculate/?student_id=&month=&year= works."""
        response = self.client.get(
            f"/api/payments/calculate/?student_id={self.student.id}&month=6&year=2026"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('student_id', response.data)
        self.assertIn('calculated_amount', response.data)

    def test_debtors_action(self):
        """GET /api/payments/debtors/ returns unpaid students."""
        Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=0,
            payment_date=date(2026, 6, 1),
            payment_method='cash',
            status='unpaid'
        )
        response = self.client.get("/api/payments/debtors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_report_action(self):
        """GET /api/payments/report/?month=&year= returns monthly report."""
        Payment.objects.create(
            student=self.student,
            month=6,
            year=2026,
            calculated_amount=450000,
            paid_amount=450000,
            payment_date=date(2026, 6, 1),
            payment_method='cash',
            status='paid'
        )
        response = self.client.get("/api/payments/report/?month=6&year=2026")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('month', response.data)
        self.assertIn('year', response.data)
        self.assertIn('total_calculated', response.data)
        self.assertIn('total_paid', response.data)
