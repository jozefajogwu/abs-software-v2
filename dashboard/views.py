from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from equipment.models import Equipment
from projects.models import Project
from incidents.models import Incident
from inventory.models import Inventory
from django.db.models import Count, Q
from django.utils.timezone import now
from safety.models import SafetyIncident
from finance.models import FinanceRecord
from django.db.models import Count, Q, Sum
from inventory.models import Inventory
from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import ListAPIView
from transaction.models import Transaction
from rest_framework.permissions import IsAuthenticated
from .serializers import TransactionSerializer
        
from activity.models import RecentActivity






from operations.models import OperationRecord, MaintenanceRecord
from django.db.models.functions import TruncDay, TruncMonth, TruncYear


User = get_user_model()

class DashboardSummary(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({
            "users": User.objects.count(),
            "project_managers": User.objects.filter(role='project_manager').count(),
            "safety_officers": User.objects.filter(role='safety_officer').count(),
            "inventory_managers": User.objects.filter(role='inventory_manager').count(),
            "accounts_managers": User.objects.filter(role='accounts_manager').count(),
            "equipment_managers": User.objects.filter(role='equipment_manager').count(),
            "equipments": Equipment.objects.count(),
            "projects": Project.objects.count(),
            "incidents": Incident.objects.count(),
            "inventory": Inventory.objects.count(),
            "operation_records": OperationRecord.objects.count(),
            "maintenance_records": MaintenanceRecord.objects.count()
        })
class OperationalSummary(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        daily = OperationRecord.objects.annotate(day=TruncDay('date')) \
            .values('day') \
            .annotate(count=Count('id')) \
            .order_by('day')

        monthly = OperationRecord.objects.annotate(month=TruncMonth('date')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        yearly = OperationRecord.objects.annotate(year=TruncYear('date')) \
            .values('year') \
            .annotate(count=Count('id')) \
            .order_by('year')

        return Response({
            "daily": list(daily),
            "monthly": list(monthly),
            "yearly": list(yearly)
        })
class MaintenanceSummary(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        daily = MaintenanceRecord.objects.annotate(day=TruncDay('performed_at')) \
            .values('day') \
            .annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                pending=Count('id', filter=Q(status='pending'))
            ) \
            .order_by('day')

        monthly = MaintenanceRecord.objects.annotate(month=TruncMonth('performed_at')) \
            .values('month') \
            .annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                pending=Count('id', filter=Q(status='pending'))
            ) \
            .order_by('month')

        yearly = MaintenanceRecord.objects.annotate(year=TruncYear('performed_at')) \
            .values('year') \
            .annotate(
                total=Count('id'),
                completed=Count('id', filter=Q(status='completed')),
                pending=Count('id', filter=Q(status='pending'))
            ) \
            .order_by('year')

        return Response({
            "daily": list(daily),
            "monthly": list(monthly),
            "yearly": list(yearly)
        })




class RecentActivityFeed(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        app_filter = request.query_params.get("app_name")
        logs = RecentActivity.objects.select_related("user").order_by("-created_at")[:20]

        if app_filter:
            logs = logs.filter(app_name=app_filter)

        activities = []
        for log in logs:
            activities.append({
                "id": log.id,
                "user": log.user.email if log.user else "System",
                "app_name": log.app_name,
                "model_name": log.model_name,
                "object_id": log.object_id,
                "action": log.get_action_display(),
                "description": log.description,
                "created_at": log.created_at.isoformat(),
            })

        return Response(activities)

class FinancialSummary(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        revenue = FinanceRecord.objects.filter(type='revenue').aggregate(total=Sum('amount'))['total'] or 0
        expenses = FinanceRecord.objects.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
        profit = revenue - expenses

        return Response({
            "revenue": revenue,
            "expenses": expenses,
            "profit": profit
        })
        
class InventoryStatus(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = Inventory.objects.count()
        status_counts = {
            "good": Inventory.objects.filter(status='good').count(),
            "average": Inventory.objects.filter(status='average').count(),
            "critical": Inventory.objects.filter(status='critical').count(),
        }

        return Response({
            "total": total,
            "status": status_counts
        })
        
class TransactionListView(ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]