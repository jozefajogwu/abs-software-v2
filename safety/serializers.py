from rest_framework import serializers
from .models import  SafetyIncident  


class SafetyIncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SafetyIncident
        fields = '__all__'
