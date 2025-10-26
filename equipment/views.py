from rest_framework import generics
from .models import Equipment
from .serializers import EquipmentSerializer
from users.permissions import IsEquipmentManager


class EquipmentListCreateView(generics.ListCreateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsEquipmentManager]


class EquipmentUpdateView(generics.UpdateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsEquipmentManager]
    lookup_field = 'id'


class EquipmentDeleteView(generics.DestroyAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsEquipmentManager]
    lookup_field = 'id'


class EquipmentDetailView(generics.RetrieveAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsEquipmentManager]
    lookup_field = 'id'
