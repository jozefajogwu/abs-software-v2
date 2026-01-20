from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Equipment
from .serializers import EquipmentSerializer
from activity.utils import log_activity


class EquipmentListCreateView(generics.ListCreateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        equipment = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="equipment",
            model_name="Equipment",
            object_id=equipment.id,
            action="create",
            description=f"Added equipment {equipment.name}"
        )


class EquipmentUpdateView(generics.UpdateAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        equipment = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="equipment",
            model_name="Equipment",
            object_id=equipment.id,
            action="update",
            description=f"Updated equipment {equipment.name}"
        )


class EquipmentDeleteView(generics.DestroyAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            app_name="equipment",
            model_name="Equipment",
            object_id=instance.id,
            action="delete",
            description=f"Deleted equipment {instance.name}"
        )
        instance.delete()
        
class EquipmentDetailView(generics.RetrieveAPIView):
    queryset = Equipment.objects.all()
    serializer_class = EquipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    


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


class EquipmentStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = Equipment.objects.count()
        available = Equipment.objects.filter(status="Available").count()
        active = Equipment.objects.filter(status="In Use").count()
        repair = Equipment.objects.filter(status="Under Maintenance").count()
        retired = Equipment.objects.filter(status="Retired").count()

        # Log activity when stats are viewed
        log_activity(
            user=request.user,
            app_name="equipment",
            model_name="Equipment",
            object_id=None,  # no specific object, it's a summary
            action="view",
            description="Viewed equipment stats"
        )

        return Response({
            "total_equipment": total,
            "available_equipment": available,
            "active_equipment": active,
            "repair_equipment": repair,
            "retired_equipment": retired
        })
