from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Student
from .serializers import StudentListSerializer, StudentSerializer
from utils.permissions import IsSuperAdmin, IsAdminOrSuperAdmin


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.filter(deleted_at__isnull=True)
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['full_name', 'phone']
    ordering_fields = ['created_at']

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsSuperAdmin()]
        return [IsAdminOrSuperAdmin()]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return StudentListSerializer
        return StudentSerializer

    def _duplicate_phone_response(self):
        return Response(
            {
                'error_code': 'DUPLICATE_ENTRY',
                'detail': 'A student with this phone number already exists.',
            },
            status=status.HTTP_409_CONFLICT,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            if 'phone' in serializer.errors:
                phone_errors = serializer.errors['phone']
                if any('DUPLICATE_PHONE' in str(e) or 'already exists' in str(e) for e in phone_errors):
                    return self._duplicate_phone_response()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # ← bu yerda group 9999 → 400
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return self._duplicate_phone_response()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            if 'phone' in serializer.errors:
                phone_errors = serializer.errors['phone']
                if any(
                    'DUPLICATE_PHONE' in str(e) or 'already exists' in str(e)
                    for e in phone_errors
                ):
                    return self._duplicate_phone_response()
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_update(serializer)
        except IntegrityError:
            return self._duplicate_phone_response()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        student = self.get_object()
        return Response(
            {
                'student_id': student.id,
                'full_name': student.full_name,
                'status': student.status,
                'message': 'Student stats placeholder.',
            }
        )
