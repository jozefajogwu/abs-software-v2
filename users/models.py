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
# RoleModulePermission: Refactored for Integer IDs
# ────────────────────────────────────────────────────────────────

class RoleModulePermission(models.Model):
    # ✅ Changed from ForeignKey(Group) to IntegerField to match CustomUser.role
    role_id = models.IntegerField() 
    module = models.CharField(max_length=50) # e.g., 'inventory', 'safety'
    
    # ✅ Updated choices to lowercase to simplify frontend mapping
    ACCESS_CHOICES = [
        ('none', 'None'),
        ('view', 'View'),
        ('edit', 'Edit'),
        ('full', 'Full'),
    ]
    access_level = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='none')

    class Meta:
        # Prevents duplicate permission entries for the same role/module combo
        unique_together = ('role_id', 'module') # 👈 COMMENTED OUT TEMPORARILY
        pass

    def __str__(self):
        # Importing here to avoid circular import if necessary
        from .models import CustomUser 
        role_name = dict(CustomUser.ROLE_CHOICES).get(self.role_id, f"Unknown Role {self.role_id}")
        return f"{role_name} - {self.module}: {self.access_level}"
# ────────────────────────────────────────────────────────────────
# Other Models
# ────────────────────────────────────────────────────────────────

class Role(models.Model):
    """Note: This model is now mostly used for metadata/descriptions since 
    CustomUser uses the IntegerField 'role' for logic."""
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