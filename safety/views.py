from django.shortcuts import render
from rest_framework import viewsets
from .models import SafetyIncident, RiskAssessment
from .serializers import SafetyIncidentSerializer, RiskAssessmentSerializer

def profile(request):
    return render(request, "account/profile.html")


# ────────────────────────────────────────────────────────────────
# Safety Incident ViewSet
# ────────────────────────────────────────────────────────────────

class SafetyIncidentViewSet(viewsets.ModelViewSet):
    queryset = SafetyIncident.objects.all()
    serializer_class = SafetyIncidentSerializer


# ────────────────────────────────────────────────────────────────
# Risk Assessment ViewSet
# ────────────────────────────────────────────────────────────────

class RiskAssessmentViewSet(viewsets.ModelViewSet):
    queryset = RiskAssessment.objects.all()
    serializer_class = RiskAssessmentSerializer
