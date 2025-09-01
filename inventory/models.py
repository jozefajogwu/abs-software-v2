from django.db import models
from users.models import CustomUser
from django.conf import settings


# Create your models here.
class Inventory(models.Model):
    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    quantity = models.IntegerField()
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,  # 👈 allows existing rows to stay empty
    blank=True  # 👈 allows admin forms to skip it
)
    unit = models.CharField(max_length=50)  # e.g., Pieces, Liters
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name

    
    