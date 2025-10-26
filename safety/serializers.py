from rest_framework import serializers
from .models import SafetyIncident, RiskAssessment


# ────────────────────────────────────────────────────────────────
# Safety Incident Serializer
# ────────────────────────────────────────────────────────────────

class SafetyIncidentSerializer(serializers.ModelSerializer):
    reported_by_username = serializers.CharField(source='reported_by.username', read_only=True)

    class Meta:
        model = SafetyIncident
        fields = [
            'id',
            'incident_date',
            'description',
            'actions_taken',
            'incident_status',
            'severity',
            'location',
            'project',
            'reported_by',
            'reported_by_username',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


# ────────────────────────────────────────────────────────────────
# Risk Assessment Serializer
# ────────────────────────────────────────────────────────────────

class RiskAssessmentSerializer(serializers.ModelSerializer):
    assessed_by_username = serializers.CharField(source='assessed_by.username', read_only=True)
    related_incident_id = serializers.IntegerField(source='related_incident.id', read_only=True)

    class Meta:
        model = RiskAssessment
        fields = [
            'id',
            'assessment_date',
            'project',
            'hazard_type',
            'status',
            'likelihood',
            'impact',
            'mitigation_plan',
            'assessed_by',
            'assessed_by_username',
            'related_incident',
            'related_incident_id',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
