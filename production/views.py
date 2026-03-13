from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.dateparse import parse_date

from .models import Operation, Maintenance, Production
from .serializers import OperationSerializer, MaintenanceSerializer, ProductionSerializer
from activity.utils import log_activity 

from users.permissions import IsProductionManager, IsProjectManager

PRODUCTION_PERMISSIONS = [IsProductionManager | IsProjectManager]

# --- Operation endpoints ---
class OperationListCreateView(generics.ListCreateAPIView):
    serializer_class = OperationSerializer
    permission_classes = PRODUCTION_PERMISSIONS 

    def get_queryset(self):
        queryset = Operation.objects.all().order_by('-date')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset

    def perform_create(self, serializer):
        operation = serializer.save()
        log_activity(user=self.request.user, app_name="production", model_name="Operation", object_id=operation.id, action="create", description=f"Created operation record on {operation.date}")

class OperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = PRODUCTION_PERMISSIONS
    lookup_field = 'id'

# --- Maintenance endpoints (MISSING CLASSES ADDED HERE) ---
class MaintenanceListCreateView(generics.ListCreateAPIView):
    serializer_class = MaintenanceSerializer
    permission_classes = PRODUCTION_PERMISSIONS

    def get_queryset(self):
        queryset = Maintenance.objects.all().order_by('-date')
        return queryset

    def perform_create(self, serializer):
        maintenance = serializer.save()
        log_activity(user=self.request.user, app_name="production", model_name="Maintenance", object_id=maintenance.id, action="create", description=f"Created maintenance record on {maintenance.date}")

class MaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = PRODUCTION_PERMISSIONS
    lookup_field = 'id'

# --- Production endpoints (MISSING CLASSES ADDED HERE) ---
class ProductionListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductionSerializer
    permission_classes = PRODUCTION_PERMISSIONS

    def get_queryset(self):
        return Production.objects.all().order_by('-date')

class ProductionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = PRODUCTION_PERMISSIONS
    lookup_field = 'id'

# --- Summary Views ---
class OperationSummaryView(APIView):
    permission_classes = PRODUCTION_PERMISSIONS
    def get(self, request):
        queryset = Operation.objects.all()
        totals = queryset.aggregate(total_income=Sum('income'), total_expenditure=Sum('expenditure'), total_balance=Sum('balance'))
        return Response({"total_income": totals['total_income'] or 0, "total_expenditure": totals['total_expenditure'] or 0, "total_balance": totals['total_balance'] or 0})

class MaintenanceSummaryView(APIView):
    permission_classes = PRODUCTION_PERMISSIONS
    def get(self, request):
        queryset = Maintenance.objects.all()
        totals = queryset.aggregate(total_income=Sum('income'), total_expenditure=Sum('expenditure'), total_balance=Sum('balance'))
        return Response({"total_income": totals['total_income'] or 0, "total_expenditure": totals['total_expenditure'] or 0, "total_balance": totals['total_balance'] or 0})