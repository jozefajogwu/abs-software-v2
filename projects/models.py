from django.db import models
from django.conf import settings
from equipment.models import Equipment
from inventory.models import Inventory

class Project(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Completed', 'Completed'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled'),
    ]

    project_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        null=True,
        blank=True
    )

    assigned_team = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='assigned_projects',
        blank=True
    )

    equipment = models.ManyToManyField(Equipment, related_name='projects', blank=True)
    inventory = models.ManyToManyField(Inventory, related_name='projects', blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name
