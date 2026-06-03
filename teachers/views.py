from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Teacher
from .serializers import TeacherListSerializer, TeacherSerializer


class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'phone', 'subject']
    ordering_fields = ['created_at']

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TeacherListSerializer
        return TeacherSerializer

    def _duplicate_response(self, field):
        return Response(
            {
                'error_code': 'DUPLICATE_ENTRY',
                'detail': f'A teacher with this {field} already exists.',
            },
            status=status.HTTP_409_CONFLICT,
        )

    def _validation_duplicate_response(self, serializer):
        if 'phone' in serializer.errors:
            phone_errors = serializer.errors['phone']
            if any(
                'DUPLICATE_PHONE' in str(error) or 'already exists' in str(error)
                for error in phone_errors
            ):
                return self._duplicate_response('phone')

        if 'email' in serializer.errors:
            email_errors = serializer.errors['email']
            if any(
                'DUPLICATE_EMAIL' in str(error) or 'already exists' in str(error)
                for error in email_errors
            ):
                return self._duplicate_response('email')

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return self._validation_duplicate_response(serializer)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return self._duplicate_response('phone or email')
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        if not serializer.is_valid():
            return self._validation_duplicate_response(serializer)
        try:
            self.perform_update(serializer)
        except IntegrityError:
            return self._duplicate_response('phone or email')
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='groups')
    def groups(self, request, pk=None):
        teacher = self.get_object()
        return Response(
            {
                'teacher_id': teacher.id,
                'full_name': teacher.full_name,
                'message': 'Teacher groups placeholder.',
            }
        )

    @action(detail=True, methods=['get'], url_path='salary')
    def salary(self, request, pk=None):
        teacher = self.get_object()
        return Response(
            {
                'teacher_id': teacher.id,
                'full_name': teacher.full_name,
                'salary_type': teacher.salary_type,
                'salary_value': str(teacher.salary_value),
                'message': 'Salary calculation placeholder.',
            }
        )
