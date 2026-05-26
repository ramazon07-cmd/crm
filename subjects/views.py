from rest_framework.viewsets import ModelViewSet
from .models import Subject
from .serializers import SubjectSerializer

class SubjectViewSet(ModelViewSet):
    queryset =  Subject.objects.all()
    serializer_class = SubjectSerializer