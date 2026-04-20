from django.contrib.auth.models import AbstractUser, Group
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        (0, 'Project Manager'),
        (1, 'Safety Officer'),
        (2, 'Inventory Manager'),
        (3, 'Production Manager'),
        (4, 'Equipment Manager'),
    )

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.IntegerField(choices=ROLE_CHOICES, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    must_change_password = models.BooleanField(
        default=False, 
        help_text="Designates whether the user must change their password upon next login."
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def role_label(self):
        """Return the human-readable label for the role integer."""
        return dict(self.ROLE_CHOICES).get(self.role)

# ────────────────────────────────────────────────────────────────
# RoleModulePermission: Fixed for Multi-Role Persistence
# ────────────────────────────────────────────────────────────────

class RoleModulePermission(models.Model):
    # Matches CustomUser.role integer IDs
    role_id = models.IntegerField() 
    module = models.CharField(max_length=50) # e.g., 'inventory', 'safety'
    
    ACCESS_CHOICES = [
        ('none', 'None'),
        ('view', 'View'),
        ('edit', 'Edit'),
        ('full', 'Full'),
    ]
    access_level = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='none')

    class Meta:
        # ✅ Re-enabled and strictly enforced:
        # This allows "inventory" for Role 0 AND "inventory" for Role 1.
        # It prevents a single role from having duplicate module entries.
        unique_together = ('role_id', 'module')

    def __str__(self):
        # Human readable string for Admin panel
        role_name = dict(CustomUser.ROLE_CHOICES).get(self.role_id, f"Unknown Role {self.role_id}")
        return f"{role_name} - {self.module}: {self.access_level}"

# ────────────────────────────────────────────────────────────────
# Other Models
# ────────────────────────────────────────────────────────────────

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    RANK_CHOICES = [
        ('Administrator', 'Administrator'),
        ('Manager', 'Manager'),
        ('Staff', 'Staff'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name