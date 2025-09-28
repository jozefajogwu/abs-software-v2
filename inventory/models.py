from django.db import models
from users.models import CustomUser
from django.conf import settings


# Create your models here.

class Inventory(models.Model):
    STATUS_CHOICES = (
        ('good', 'Good'),
        ('average', 'Average'),
        ('critical', 'Critical'),
    )

    item_name = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)  # e.g., Pieces, Liters
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='good')  # 👈 NEW
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name
