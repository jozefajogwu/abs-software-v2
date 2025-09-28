from django.db import models
from equipment.models import Equipment


class OperationRecord(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    operator = models.CharField(max_length=100)
    date = models.DateField()
    hours_used = models.DecimalField(max_digits=5, decimal_places=2)
    activity = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('completed', 'Completed'), ('pending', 'Pending')])

    
class MaintenanceRecord(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    description = models.TextField()
    performed_at = models.DateField()
    status = models.CharField(max_length=20, choices=[('completed', 'Completed'), ('pending', 'Pending')])

