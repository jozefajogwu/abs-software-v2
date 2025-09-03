"""
This module contains the models for safety incidents.
"""

from django.db import models
from users.models import CustomUser
from django.conf import settings

# Create your models here.

class SafetyIncident(models.Model):
    incident_date = models.DateField()
    description = models.TextField()
    actions_taken = models.TextField()
    incident_status = models.CharField(max_length=50)
 
    reported_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,   # ✅ allows existing rows to stay empty
    blank=True,  # ✅ allows admin forms to skip it
    related_name='safety_reports'
)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.incident_date} - {self.incident_status}"
    
    
    #user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
