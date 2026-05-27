from rest_framework.viewsets import ModelViewSet
from .models import Grade
from .serializers import GradeSerializer
from utils.permissions import IsAdminOrReadOnly


class GradeViewSet(ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsAdminOrReadOnly]
