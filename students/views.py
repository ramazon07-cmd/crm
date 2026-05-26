from rest_framework.viewsets import ModelViewSet
from .models import Student
from .serializers import StudentSerializer
from utils.permissions import IsAdminOrReadOnly

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly] 