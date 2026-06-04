from django.db import IntegrityError
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Attendance, Holiday
from .serializers import (
    AttendanceListSerializer,
    AttendanceSerializer,
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            # unique_together xatosi non_field_errors ga tushadi
            if 'non_field_errors' in serializer.errors:
                return self._duplicate_entry_response()
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            return self._duplicate_entry_response()
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('group_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date'),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class HolidayViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    ordering_fields = ['date']
