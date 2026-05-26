from rest_framework.viewsets import ModelViewSet
from .models import Subject
from .serializers import SubjectSerializer
from utils.permissions import IsAdminOrReadOnly

class SubjectViewSet(ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly] 