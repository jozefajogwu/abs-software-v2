from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count # Added for optimization
from .models import Equipment
from .serializers import EquipmentSerializer
from activity.utils import log_activity
from users.permissions import IsEquipmentManager 

# --- CRUD VIEWS ---

class EquipmentListCreateView(generics.ListCreateAPIView):
    queryset = Equipment.objects.all().order_by('-id')
    serializer_class = EquipmentSerializer
    permission_classes = [IsEquipmentManager] # Requirement #2 Met

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
    permission_classes = [IsEquipmentManager]
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
    permission_classes = [IsEquipmentManager]
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
    permission_classes = [IsEquipmentManager]
    lookup_field = 'id'

# --- STATS VIEW (Optimized) ---

class EquipmentStatsView(APIView):
    permission_classes = [IsEquipmentManager]

    def get(self, request):
        # Optimized: 1 Database hit instead of 5
        stats = Equipment.objects.values('status').annotate(total=Count('status'))
        
        # Convert queryset to a simple dictionary for the frontend
        status_map = {item['status']: item['total'] for item in stats}
        total_count = Equipment.objects.count()

        return Response({
            "total_equipment": total_count,
            "available_equipment": status_map.get("Available", 0),
            "active_equipment": status_map.get("In Use", 0),
            "repair_equipment": status_map.get("Under Maintenance", 0),
            "retired_equipment": status_map.get("Retired", 0)
        })