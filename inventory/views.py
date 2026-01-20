from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils.dateparse import parse_date
from .models import Inventory
from .serializers import InventorySerializer
from activity.utils import log_activity   # <-- import the logger


# --- CRUD Endpoints ---
class InventoryListCreateView(generics.ListCreateAPIView):
    serializer_class = InventorySerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]
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
    permission_classes = [IsAuthenticated]

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

        # Example: flag items with quantity < 10 as "low stock"
        low_stock_items = queryset.filter(quantity__lt=10)
        critical_items = queryset.filter(status='critical')

        return Response({
            "total_stock": total_stock,
            "low_stock_alerts": InventorySerializer(low_stock_items, many=True).data,
            "critical_items": InventorySerializer(critical_items, many=True).data
        })
