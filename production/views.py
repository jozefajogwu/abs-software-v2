from django.shortcuts import render

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Operation, Maintenance, Production
from .serializers import OperationSerializer, MaintenanceSerializer, ProductionSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from .models import Operation, Maintenance

# Operation endpoints
class OperationListCreateView(generics.ListCreateAPIView):
    queryset = Operation.objects.all().order_by('-date')
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]

class OperationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


# Maintenance endpoints
class MaintenanceListCreateView(generics.ListCreateAPIView):
    queryset = Maintenance.objects.all().order_by('-date')
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]

class MaintenanceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


# Production endpoints
class ProductionListCreateView(generics.ListCreateAPIView):
    queryset = Production.objects.all().order_by('-date')
    serializer_class = ProductionSerializer
    permission_classes = [IsAuthenticated]

class ProductionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


#Summary Views


class OperationSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        totals = Operation.objects.aggregate(
            total_income=Sum('income'),
            total_expenditure=Sum('expenditure'),
            total_balance=Sum('balance')
        )
        return Response(totals)


class MaintenanceSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        totals = Maintenance.objects.aggregate(
            total_income=Sum('income'),
            total_expenditure=Sum('expenditure'),
            total_balance=Sum('balance')
        )
        return Response(totals)
