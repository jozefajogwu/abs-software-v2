from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsProductionManager
from .models import Operation
from .serializers import OperationSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F
from .models import MaintenanceRecord
from .serializers import MaintenanceRecordSerializer
from users.permissions import IsProductionManager


# Create your views here.

class OperationListCreateView(generics.ListCreateAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsProductionManager]


class OperationDetailView(generics.RetrieveAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsProductionManager]
    lookup_field = 'id'


class OperationUpdateView(generics.UpdateAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsProductionManager]
    lookup_field = 'id'


class OperationDeleteView(generics.DestroyAPIView):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer
    permission_classes = [IsProductionManager]
    lookup_field = 'id'

class OperationSummaryView(APIView):
    permission_classes = [IsProductionManager]

    def get(self, request):
        total_income = Operation.objects.aggregate(total=Sum('income'))['total'] or 0
        total_expenses = Operation.objects.aggregate(total=Sum('expenses'))['total'] or 0
        balance = total_income - total_expenses

        return Response({
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance
        })

class MaintenanceRecordListCreateView(generics.ListCreateAPIView):
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsProductionManager]


class MaintenanceRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MaintenanceRecord.objects.all()
    serializer_class = MaintenanceRecordSerializer
    permission_classes = [IsProductionManager]
    lookup_field = 'id'