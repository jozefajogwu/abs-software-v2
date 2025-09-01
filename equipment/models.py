from django.db import models
from users.models import CustomUser

# Create your models here.
class Equipment(models.Model):
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    purchase_date = models.DateField()
    purchase_cost = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=50)  # Available, In Use, Under Maintenance, Retired
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.equipment_name)
        
