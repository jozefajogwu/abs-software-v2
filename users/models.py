from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=50, choices=[
        ('project_manager', 'Project Manager'),
        ('safety_officer', 'Safety Officer'),
        ('inventory_manager', 'Inventory Manager'),
        ('accounts_manager', 'Accounts Manager'),
        ('equipment_manager', 'Equipment Manager'),
        
    ], blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email']  # Optional: forces email during user creation

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
