from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.timezone import now
from datetime import timedelta

from .models import SafetyIncident, RiskAssessment
from .serializers import SafetyIncidentSerializer, RiskAssessmentSerializer


def profile(request):
    return render(request, "account/profile.html")


# ────────────────────────────────────────────────────────────────
# Safety Incident ViewSet with Stats Action
# ────────────────────────────────────────────────────────────────



class SafetyIncidentViewSet(viewsets.ModelViewSet):
    queryset = SafetyIncident.objects.all()
    serializer_class = SafetyIncidentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Automatically set reported_by to the authenticated user
        when creating a new incident.
        """
        serializer.save(reported_by=self.request.user)

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
# Risk Assessment ViewSet
# ────────────────────────────────────────────────────────────────

class RiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
