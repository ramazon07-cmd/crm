from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from utils.permissions import IsAdminOrReadOnly


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=['get'])
    def unpaid(self, request):
        queryset = self.get_queryset().filter(status=Payment.Status.UNPAID)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
