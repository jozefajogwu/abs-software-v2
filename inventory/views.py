from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, F
from .models import Inventory
from .serializers import InventorySerializer
from users.permissions import IsInventoryManager

class InventoryListCreateView(generics.ListCreateAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsInventoryManager]

class InventoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inventory.objects.all()
    serializer_class = InventorySerializer
    permission_classes = [IsInventoryManager]
    lookup_field = 'id'

class InventorySummaryView(APIView):
    permission_classes = [IsInventoryManager]
     
     
    def get(self, request):
        total_stock = Inventory.objects.aggregate(total=Sum('quantity'))['total'] or 0
        low_stock_items = Inventory.objects.filter(quantity__lte=F('quantity') * 0.2)
        critical_items = Inventory.objects.filter(status='critical')
        low_stock_data = InventorySerializer(low_stock_items, many=True).data
        critical_data = InventorySerializer(critical_items, many=True).data

        return Response({
            "total_stock": total_stock,
            "low_stock_alerts": low_stock_data,
            "critical_items": critical_data
        })
