from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count # Added Count
from django.utils.dateparse import parse_date
from .models import Inventory
from .serializers import InventorySerializer
from activity.utils import log_activity 
from users.permissions import IsInventoryManager # ✅ Imported

# --- CRUD Endpoints ---
class InventoryListCreateView(generics.ListCreateAPIView):
    serializer_class = InventorySerializer
    # ✅ FIX: Requirement #2 - Lock it to Inventory Managers only
    permission_classes = [IsInventoryManager]

    def get_queryset(self):
        queryset = Inventory.objects.all().order_by('-created_at')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(created_at__date__range=[start_date, end_date])
        return queryset

    def perform_create(self, serializer):
        # Ensure user is passed if your model requires it
        item = serializer.save(user=self.request.user)
        log_activity(
            user=self.request.user,
            app_name="inventory",
            model_name="Inventory",
            object_id=item.id,
            action="create",
            description=f"Added inventory item {item.item_name}"
        )

class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    # ✅ FIX: Requirement #2 - Lock it down
    permission_classes = [IsInventoryManager]
    lookup_field = 'id'

    def perform_update(self, serializer):
        item = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="inventory",
            model_name="Inventory",
            object_id=item.id,
            action="update",
            description=f"Updated inventory item {item.item_name}"
        )

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            app_name="inventory",
            model_name="Inventory",
            object_id=instance.id,
            action="delete",
            description=f"Deleted inventory item {instance.item_name}"
        )
        instance.delete()

# --- Summary Endpoint ---
class InventorySummaryView(APIView):
    # ✅ FIX: Lock the summary to Inventory Managers
    permission_classes = [IsInventoryManager]

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        queryset = Inventory.objects.all()

        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(created_at__date__range=[start_date, end_date])

        total_stock = queryset.aggregate(total=Sum('quantity'))['total'] or 0
        low_stock_items = queryset.filter(quantity__lt=10)
        critical_items = queryset.filter(status='critical')

        return Response({
            "total_stock": total_stock,
            "low_stock_alerts": InventorySerializer(low_stock_items, many=True).data,
            "critical_items": InventorySerializer(critical_items, many=True).data
        })

# --- Status Endpoint (Optimized) ---
class InventoryStatus(APIView):
    permission_classes = [IsInventoryManager]

    def get(self, request):
        # Optimized: 1 Database hit to get all counts at once
        stats = Inventory.objects.values('status').annotate(total=Count('status'))
        status_map = {item['status']: item['total'] for item in stats}
        
        return Response({
            "total": Inventory.objects.count(),
            "status": {
                "good": status_map.get('good', 0),
                "average": status_map.get('average', 0),
                "critical": status_map.get('critical', 0),
            }
        })