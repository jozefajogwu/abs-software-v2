from django.shortcuts import render
from rest_framework import viewsets
from .models import SafetyIncident
from .serializers import SafetyIncidentSerializer

def profile(request):
    return render(request, "account/profile.html")

class SafetyIncidentViewSet(viewsets.ModelViewSet):
    queryset = SafetyIncident.objects.all()
    serializer_class = SafetyIncidentSerializer
