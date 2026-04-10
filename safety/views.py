from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Count # Added for optimization

from .models import SafetyIncident, RiskAssessment
from .serializers import SafetyIncidentSerializer, RiskAssessmentSerializer
from activity.utils import log_activity
from rest_framework.views import APIView
from users.permissions import IsSafetyOfficer # ✅ Correctly imported

# ────────────────────────────────────────────────────────────────
# Safety Incident ViewSet
# ────────────────────────────────────────────────────────────────

class SafetyIncidentViewSet(viewsets.ModelViewSet):
    queryset = SafetyIncident.objects.all().order_by('-incident_date')
    serializer_class = SafetyIncidentSerializer
    # ✅ FIX: Requirement #2 - Lock down to Safety Officers only
    permission_classes = [IsSafetyOfficer]

    def perform_create(self, serializer):
        # Automatically set the reporter to the logged-in user
        incident = serializer.save(reported_by=self.request.user)
        log_activity(
            user=self.request.user,
            app_name="safety",
            model_name="SafetyIncident",
            object_id=incident.id,
            action="create",
            description=f"Created safety incident: {incident.title}"
        )

    def perform_update(self, serializer):
        incident = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="safety",
            model_name="SafetyIncident",
            object_id=incident.id,
            action="update",
            description=f"Updated safety incident: {incident.title}"
        )

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            app_name="safety",
            model_name="SafetyIncident",
            object_id=instance.id,
            action="delete",
            description=f"Deleted safety incident: {instance.title}"
        )
        instance.delete()

    @action(detail=False, methods=['get'], url_path='stats')
    def stats(self, request):
        thirty_days_ago = now().date() - timedelta(days=30)
        
        # Optimized: Get status counts in one database hit
        status_stats = SafetyIncident.objects.values('incident_status').annotate(total=Count('incident_status'))
        status_map = {item['incident_status']: item['total'] for item in status_stats}
        
        total = SafetyIncident.objects.count()
        recent = SafetyIncident.objects.filter(incident_date__gte=thirty_days_ago).count()

        return Response({
            "total_incidents": total,
            "recent_incidents": recent,
            "resolved_incidents": status_map.get("resolved", 0),
            "investigating_incidents": status_map.get("investigating", 0),
            "open_incidents": status_map.get("open", 0) # Added to match your summary
        })


# ────────────────────────────────────────────────────────────────
# Risk Assessment ViewSet
# ────────────────────────────────────────────────────────────────

class RiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = RiskAssessment.objects.all().order_by('-id')
    serializer_class = RiskAssessmentSerializer
    # ✅ FIX: Requirement #2 - Lock down
    permission_classes = [IsSafetyOfficer]

    def perform_create(self, serializer):
        assessment = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="safety",
            model_name="RiskAssessment",
            object_id=assessment.id,
            action="create",
            description=f"Created risk assessment: {assessment.title}"
        )

    def perform_update(self, serializer):
        assessment = serializer.save()
        log_activity(
            user=self.request.user,
            app_name="safety",
            model_name="RiskAssessment",
            object_id=assessment.id,
            action="update",
            description=f"Updated risk assessment: {assessment.title}"
        )

    def perform_destroy(self, instance):
        log_activity(
            user=self.request.user,
            app_name="safety",
            model_name="RiskAssessment",
            object_id=instance.id,
            action="delete",
            description=f"Deleted risk assessment: {instance.title}"
        )
        instance.delete()
        

# ────────────────────────────────────────────────────────────────
# Safety Summary Endpoint
# ────────────────────────────────────────────────────────────────

class SafetySummary(APIView):
    permission_classes = [IsSafetyOfficer]

    def get(self, request):
        # Optimized database hit
        stats = SafetyIncident.objects.values('incident_status').annotate(total=Count('incident_status'))
        status_map = {item['incident_status']: item['total'] for item in stats}

        return Response({
            "total_incidents": SafetyIncident.objects.count(),
            "open_incidents": status_map.get("open", 0),
            "closed_incidents": status_map.get("resolved", 0) # Resolved/Closed mapping
        })