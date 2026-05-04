from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count  # ✅ Added Count here
from django.utils.dateparse import parse_date

# Added the new DailyProductionRecord model and serializer
from .models import Operation, Maintenance, Production, DailyProductionRecord
from .serializers import OperationSerializer, MaintenanceSerializer, ProductionSerializer, DailyProductionRecordSerializer
from activity.utils import log_activity 
from users.permissions import IsProductionManager, IsProjectManager

# ✅ Fix: Proper OR syntax for permission classes
PRODUCTION_PERMISSIONS = [(IsProductionManager | IsProjectManager)]

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

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(user=self.request.user, app_name="production", model_name="Operation", object_id=obj.id, action="update", description=f"Updated operation record {obj.id}")

    def perform_destroy(self, instance):
        log_activity(user=self.request.user, app_name="production", model_name="Operation", object_id=instance.id, action="delete", description=f"Deleted operation record from {instance.date}")
        instance.delete()


# --- Maintenance endpoints ---
class MaintenanceListCreateView(generics.ListCreateAPIView):
    serializer_class = MaintenanceSerializer
    permission_classes = PRODUCTION_PERMISSIONS

    def get_queryset(self):
        return Maintenance.objects.all().order_by('-date')

    def perform_create(self, serializer):
        maintenance = serializer.save()
        log_activity(user=self.request.user, app_name="production", model_name="Maintenance", object_id=maintenance.id, action="create", description=f"Created maintenance record on {maintenance.date}")

class MaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = PRODUCTION_PERMISSIONS
    lookup_field = 'id'


# --- Production endpoints (Trucks/Haulage) ---
class ProductionListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductionSerializer
    permission_classes = PRODUCTION_PERMISSIONS

    def get_queryset(self):
        return Production.objects.all().order_by('-date')

    def perform_create(self, serializer):
        prod = serializer.save()
        log_activity(user=self.request.user, app_name="production", model_name="Production", object_id=prod.id, action="create", description=f"Created production entry for {prod.date}")

class ProductionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = PRODUCTION_PERMISSIONS
    lookup_field = 'id'


# --- NEW: Daily Production Records (Physical Work/Efficiency) ---
class DailyProductionRecordListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyProductionRecordSerializer
    permission_classes = PRODUCTION_PERMISSIONS

    def get_queryset(self):
        # Order by newest first
        queryset = DailyProductionRecord.objects.all().order_by('-date', '-created_at')
        
        # Allows the frontend to filter by day (e.g., ?date=2026-04-28)
        specific_date = self.request.query_params.get('date')
        if specific_date:
            parsed_date = parse_date(specific_date)
            if parsed_date:
                queryset = queryset.filter(date=parsed_date)
        return queryset

    def perform_create(self, serializer):
        # Save the record and automatically attach the logged-in user
        record = serializer.save(logged_by=self.request.user)
        log_activity(user=self.request.user, app_name="production", model_name="DailyProductionRecord", object_id=record.id, action="create", description=f"Logged daily production for {record.item_name}")

class DailyProductionRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = DailyProductionRecord.objects.all()
    serializer_class = DailyProductionRecordSerializer
    permission_classes = PRODUCTION_PERMISSIONS
    lookup_field = 'id'

    def perform_update(self, serializer):
        obj = serializer.save()
        log_activity(user=self.request.user, app_name="production", model_name="DailyProductionRecord", object_id=obj.id, action="update", description=f"Updated daily production record {obj.id}")

    def perform_destroy(self, instance):
        log_activity(user=self.request.user, app_name="production", model_name="DailyProductionRecord", object_id=instance.id, action="delete", description=f"Deleted daily production record from {instance.date}")
        instance.delete()


# --- Summary Views ---
class OperationSummaryView(APIView):
    permission_classes = PRODUCTION_PERMISSIONS
    
    def get(self, request):
        queryset = Operation.objects.all()
        
        # ✅ Added date filtering
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])

        # ✅ Added record count
        totals = queryset.aggregate(
            total_income=Sum('income'), 
            total_expenditure=Sum('expenditure'), 
            total_balance=Sum('balance'),
            record_count=Count('id')
        )
        
        return Response({
            "total_income": totals['total_income'] or 0, 
            "total_expenditure": totals['total_expenditure'] or 0, 
            "total_balance": totals['total_balance'] or 0,
            "operation_count": totals['record_count'] or 0
        })

class MaintenanceSummaryView(APIView):
    permission_classes = PRODUCTION_PERMISSIONS
    
    def get(self, request):
        queryset = Maintenance.objects.all()
        
        # ✅ Added date filtering
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])

        # ✅ Added record count
        totals = queryset.aggregate(
            total_income=Sum('income'), 
            total_expenditure=Sum('expenditure'), 
            total_balance=Sum('balance'),
            record_count=Count('id')
        )
        
        return Response({
            "total_income": totals['total_income'] or 0, 
            "total_expenditure": totals['total_expenditure'] or 0, 
            "total_balance": totals['total_balance'] or 0,
            "maintenance_count": totals['record_count'] or 0
        })

class DailyProductionRecordSummaryView(APIView):
    permission_classes = PRODUCTION_PERMISSIONS
    
    def get(self, request):
        queryset = DailyProductionRecord.objects.all()
        
        # Allow the frontend to filter the summary by a specific day
        specific_date = request.query_params.get('date')
        if specific_date:
            parsed_date = parse_date(specific_date)
            if parsed_date:
                queryset = queryset.filter(date=parsed_date)

        # Calculate the totals
        totals = queryset.aggregate(
            total_target=Sum('target_quantity'),
            total_actual=Sum('actual_quantity'),
            total_defective=Sum('defective_quantity')
        )
        
        total_target = totals['total_target'] or 0
        total_actual = totals['total_actual'] or 0
        total_defective = totals['total_defective'] or 0
        
        # Calculate overall efficiency for the day
        overall_efficiency = 0
        if total_target > 0:
            overall_efficiency = round((total_actual / total_target) * 100, 2)

        return Response({
            "total_target": total_target,
            "total_actual": total_actual,
            "total_defective": total_defective,
            "overall_efficiency": overall_efficiency
        })