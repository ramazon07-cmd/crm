from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Subject
from .serializers import SubjectSerializer, SubjectListSerializer


class SubjectViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        return Subject.objects.filter(deleted_at__isnull=True).order_by('-created_at')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return SubjectListSerializer
        return SubjectSerializer

    def _duplicate_response(self):
        return Response(
            {
                'error_code': 'DUPLICATE_ENTRY',
                'detail': 'A subject with this title already exists.',
            },
            status=status.HTTP_409_CONFLICT,
        )

    def _check_duplicate_error(self, errors):
        """Check if error contains DUPLICATE_TITLE."""
        if 'title' in errors:
            error_list = errors['title']
            for error in error_list:
                error_str = str(error)
                if 'DUPLICATE_TITLE' in error_str or 'already' in error_str.lower():
                    return True
        return False

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            if self._check_duplicate_error(serializer.errors):
                return self._duplicate_response()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return self._duplicate_response()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            if self._check_duplicate_error(serializer.errors):
                return self._duplicate_response()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer.save()
        except IntegrityError:
            return self._duplicate_response()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['deleted_at'])
        return Response(status=status.HTTP_204_NO_CONTENT) 