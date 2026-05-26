from rest_framework.viewsets import ModelViewSet
from .models import Teacher
from .serializers import TeacherSerializer
from utils.permissions import IsAdminOrReadOnly

class TeacherViewSet(ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrReadOnly] 