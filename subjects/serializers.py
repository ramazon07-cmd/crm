from rest_framework import serializers
from django.utils import timezone
from .models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_title(self, value):
        value = value.strip() if value else value
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) < 2:
            raise serializers.ValidationError("Title must be at least 2 characters.")
        if len(value) > 100:
            raise serializers.ValidationError("Title must be at most 100 characters.")

        # Check for duplicate among non-deleted subjects
        existing = Subject.objects.filter(
            title=value,
            deleted_at__isnull=True
        ).exclude(id=self.instance.id if self.instance else None)

        if existing.exists():
            raise serializers.ValidationError("DUPLICATE_TITLE")

        return value

    def validate_description(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("Description must be at most 500 characters.")
        return value

    def create(self, validated_data):
        return Subject.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SubjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'created_at']