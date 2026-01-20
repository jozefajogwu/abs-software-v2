from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.dateparse import parse_date

from .models import Operation, Maintenance, Production
from .serializers import OperationSerializer, MaintenanceSerializer, ProductionSerializer
from activity.utils import log_activity   # <-- import logger


# --- Operation endpoints ---
class OperationListCreateView(generics.ListCreateAPIView):
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]

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
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Operation",
            object_id=operation.id,
            action="create",
            description=f"Created operation record on {operation.date}"
        )


class OperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        operation = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Operation",
            object_id=operation.id,
            action="update",
            description=f"Updated operation record on {operation.date}"
        )

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Operation",
            object_id=instance.id,
            action="delete",
            description=f"Deleted operation record on {instance.date}"
        )
        instance.delete()


# --- Maintenance endpoints ---
class MaintenanceListCreateView(generics.ListCreateAPIView):
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Maintenance.objects.all().order_by('-date')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset

    def perform_create(self, serializer):
        maintenance = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Maintenance",
            object_id=maintenance.id,
            action="create",
            description=f"Created maintenance record on {maintenance.date}"
        )


class MaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        maintenance = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Maintenance",
            object_id=maintenance.id,
            action="update",
            description=f"Updated maintenance record on {maintenance.date}"
        )

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Maintenance",
            object_id=instance.id,
            action="delete",
            description=f"Deleted maintenance record on {instance.date}"
        )
        instance.delete()


# --- Production endpoints ---
class ProductionListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Production.objects.all().order_by('-date')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])
        return queryset

    def perform_create(self, serializer):
        production = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Production",
            object_id=production.id,
            action="create",
            description=f"Created production record on {production.date}"
        )


class ProductionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        production = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Production",
            object_id=production.id,
            action="update",
            description=f"Updated production record on {production.date}"
        )

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            app_name="production",
            model_name="Production",
            object_id=instance.id,
            action="delete",
            description=f"Deleted production record on {instance.date}"
        )
        instance.delete()


# --- Summary Views ---
class OperationSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        queryset = Operation.objects.all()

        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])

        totals = queryset.aggregate(
            total_income=Sum('income'),
            total_expenditure=Sum('expenditure'),
            total_balance=Sum('balance')
        )

        # Log summary view
        log_activity(
            user=request.user,
            app_name="production",
            model_name="Operation",
            object_id=None,
            action="view",
            description="Viewed operation summary"
        )

        return Response(totals)


class MaintenanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        queryset = Maintenance.objects.all()

        if start and end:
            start_date = parse_date(start)
            end_date = parse_date(end)
            if start_date and end_date:
                queryset = queryset.filter(date__range=[start_date, end_date])

        totals = queryset.aggregate(
            total_income=Sum('income'),
            total_expenditure=Sum('expenditure'),
            total_balance=Sum('balance')
        )

        # Log summary view
        log_activity(
            user=request.user,
            app_name="production",
            model_name="Maintenance",
            object_id=None,
            action="view",
            description="Viewed maintenance summary"
        )

        return Response(totals)
