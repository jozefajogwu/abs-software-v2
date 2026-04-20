from rest_framework import generics
from .models import ActivityLog
from .serializers import ActivityLogSerializer

class RecentActivityView(generics.ListAPIView):
    """Main Dashboard: Only Mutations"""
    serializer_class = ActivityLogSerializer
    def get_queryset(self):
        return ActivityLog.objects.filter(is_mutation=True)[:20]

class AuditLogView(generics.ListAPIView):
    """Full Audit Log: Everything (GETs, Views, etc.)"""
    serializer_class = ActivityLogSerializer
    queryset = ActivityLog.objects.all()