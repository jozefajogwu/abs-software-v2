from django.db import models
from django.conf import settings

# ────────────────────────────────────────────────────────────────
# Safety Incident Model
# ────────────────────────────────────────────────────────────────

class SafetyIncident(models.Model):
    incident_date = models.DateField()
    description = models.TextField()
    actions_taken = models.TextField()
    
    STATUS_CHOICES = [
        ("reported", "Reported"),
        ("resolving", "Resolving"),
        ("resolved", "Resolved"),
    ]
    incident_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="reported")

    severity = models.CharField(max_length=20, choices=[
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical")
    ], default="medium")

    location = models.CharField(max_length=100, blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='safety_reports'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Incident on {self.incident_date} – {self.incident_status}"


# ────────────────────────────────────────────────────────────────
# Risk Assessment Model
# ────────────────────────────────────────────────────────────────

class RiskAssessment(models.Model):
    assessment_date = models.DateField()
    project = models.CharField(max_length=100)
    hazard_type = models.CharField(max_length=100)

    STATUS_CHOICES = [
        ("reported", "Reported"),
        ("resolving", "Resolving"),
        ("mitigated", "Mitigated"),
        ("pending", "Pending"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="reported")

    likelihood = models.CharField(max_length=20, choices=[
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High")
    ], default="medium")

    impact = models.CharField(max_length=20, choices=[
        ("minor", "Minor"),
        ("moderate", "Moderate"),
        ("severe", "Severe")
    ], default="moderate")

    mitigation_plan = models.TextField(blank=True, null=True)
    assessed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="risk_assessments"
    )

    related_incident = models.ForeignKey(
        SafetyIncident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_risk_assessments"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project} – {self.hazard_type} ({self.status})"
