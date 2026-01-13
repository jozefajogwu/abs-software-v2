from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from django.utils.dateparse import parse_date

from .models import Operation, Maintenance, Production
from .serializers import OperationSerializer, MaintenanceSerializer, ProductionSerializer


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


class OperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


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


class MaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


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


class ProductionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


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
        return Response(totals)
