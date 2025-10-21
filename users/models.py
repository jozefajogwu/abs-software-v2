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
    
    # --- ADD THIS NEW FIELD ---
    must_change_password = models.BooleanField(default=False, 
                                               help_text="Designates whether the user must change their password upon next login.")
    # --------------------------

    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # Keep username required if needed

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    #creating a role model dynamically
class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
