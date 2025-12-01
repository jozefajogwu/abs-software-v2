from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Equipment
from .serializers import EquipmentSerializer


class EquipmentListCreateView(generics.ListCreateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]


class EquipmentUpdateView(generics.UpdateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    # Allow partial updates (PATCH)
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class EquipmentDeleteView(generics.DestroyAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class EquipmentDetailView(generics.RetrieveAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


# 📊 Stats Endpoint
class EquipmentStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = Equipment.objects.count()
        available = Equipment.objects.filter(status="Available").count()
        active = Equipment.objects.filter(status="In Use").count()
        repair = Equipment.objects.filter(status="Under Maintenance").count()
        retired = Equipment.objects.filter(status="Retired").count()

        return Response({
            "total_equipment": total,
            "available_equipment": available,
            "active_equipment": active,
            "repair_equipment": repair,
            "retired_equipment": retired
        })
