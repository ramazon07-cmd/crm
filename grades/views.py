from rest_framework.viewsets import ModelViewSet
from .models import Grade
from .serializers import GradeSerializer
from utils.permissions import IsAdminOrReadOnly
from users.utils import create_audit_log


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        instance = serializer.save()
        create_audit_log(self.request, 'CREATE', instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        create_audit_log(self.request, 'UPDATE', instance)

    def perform_destroy(self, instance):
        create_audit_log(self.request, 'DELETE', instance)
        instance.delete()
