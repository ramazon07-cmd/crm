from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_401_UNAUTHORIZED
)
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, AuditLog
from .serializers import UserSerializer, LoginSerializer, UserDetailSerializer, AuditLogSerializer
from utils.permissions import IsSuperAdmin


class UserViewSet(GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={201: UserDetailSerializer}
    )
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            requested_role = request.data.get('role', 'ADMIN')
            
            # SUPER_ADMIN faqat boshqa SUPER_ADMIN yarata oladi
            # LEKIN birinchi SUPER_ADMIN bo'lmasa — ruxsat ber
            if requested_role == 'SUPER_ADMIN':
                super_admin_exists = User.objects.filter(role='SUPER_ADMIN').exists()
                if super_admin_exists:
                    # Boshqa SUPER_ADMIN bor — faqat authenticated SUPER_ADMIN yarata oladi
                    if not request.user.is_authenticated or request.user.role != 'SUPER_ADMIN':
                        requested_role = 'ADMIN'
                # Agar SUPER_ADMIN yo'q bo'lsa — birinchisini yaratishga ruxsat

            serializer.validated_data['role'] = requested_role
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserDetailSerializer(user).data,
                'token': token.key
            }, status=HTTP_201_CREATED)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: UserDetailSerializer}
    )
    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'error': 'Invalid credentials'}, status=HTTP_401_UNAUTHORIZED)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserDetailSerializer(user).data,
            'token': token.key
        }, status=HTTP_200_OK)

    @swagger_auto_schema(method='put', request_body=UserSerializer, responses={200: UserDetailSerializer})
    @swagger_auto_schema(method='patch', request_body=UserSerializer, responses={200: UserDetailSerializer})
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        partial = request.method == 'PATCH'
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=partial
        )
        if serializer.is_valid():
            serializer.save()
            return Response(UserDetailSerializer(request.user).data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(responses={200: 'Logged out successfully'})
    @action(detail=False, methods=['post'])
    def logout(self, request):
        Token.objects.filter(user=request.user).delete()

        return Response(
            {'message': 'Logged out'},
            status=HTTP_200_OK
        )


class AuditLogViewSet(ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('model_name', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                enum=['Student', 'Teacher', 'Payment', 'Attendance', 'Group', 'Subject']),
            openapi.Parameter('action', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                enum=['CREATE', 'UPDATE', 'DELETE']),
            openapi.Parameter('user_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
            openapi.Parameter('object_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        model_name = self.request.query_params.get('model_name')
        action_type = self.request.query_params.get('action')
        user_id = self.request.query_params.get('user_id')
        object_id = self.request.query_params.get('object_id')

        if model_name:
            queryset = queryset.filter(model_name=model_name)
        if action_type:
            queryset = queryset.filter(action=action_type)
        if user_id:
            try:
                queryset = queryset.filter(user_id=int(user_id))
            except ValueError:
                pass
        if object_id:
            try:
                queryset = queryset.filter(object_id=int(object_id))
            except ValueError:
                pass

        return queryset