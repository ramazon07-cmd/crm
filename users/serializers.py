from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username',
            'first_name', 'last_name',
            'phone_number', 'password'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate_email(self, value): 
        user = self.instance
        if User.objects.exclude(
            pk=user.pk if user else None
        ).filter(email=value).exists():
            raise serializers.ValidationError(
                "Bu email allaqachon ro'yxatdan o'tgan."
            )
        return value

    def validate_phone_number(self, value):  
        if value:
            user = self.instance
            if User.objects.exclude(
                pk=user.pk if user else None
            ).filter(phone_number=value).exists():
                raise serializers.ValidationError(
                    "Bu telefon raqam allaqachon ro'yxatdan o'tgan."
                )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserDetailSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username',
            'first_name', 'last_name', 'full_name',
            'phone_number', 'avatar',
            'is_verified', 'created_at'  # ✅ date_joined → created_at
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']