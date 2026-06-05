from rest_framework.viewsets import GenericViewSet
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

from .models import User
from .serializers import UserSerializer, LoginSerializer, UserDetailSerializer


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