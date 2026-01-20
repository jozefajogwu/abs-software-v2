from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import timedelta

from .models import SafetyIncident, RiskAssessment
from .serializers import SafetyIncidentSerializer, RiskAssessmentSerializer
from activity.utils import log_activity   # <-- import logger


def profile(request):
    return render(request, "account/profile.html")


# ────────────────────────────────────────────────────────────────
# Safety Incident ViewSet with Stats Action + Activity Logging
# ────────────────────────────────────────────────────────────────

class SafetyIncidentViewSet(viewsets.ModelViewSet):
    queryset = SafetyIncident.objects.all()
    serializer_class = SafetyIncidentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
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
        total = SafetyIncident.objects.count()
        thirty_days_ago = now().date() - timedelta(days=30)
        recent = SafetyIncident.objects.filter(incident_date__gte=thirty_days_ago).count()
        resolved = SafetyIncident.objects.filter(incident_status="resolved").count()
        investigating = SafetyIncident.objects.filter(incident_status="investigating").count()

        return Response({
            "total_incidents": total,
            "recent_incidents": recent,
            "resolved_incidents": resolved,
            "investigating_incidents": investigating
        })


# ────────────────────────────────────────────────────────────────
# Risk Assessment ViewSet with Activity Logging
# ────────────────────────────────────────────────────────────────

class RiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
    permission_classes = [IsAuthenticated]

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
