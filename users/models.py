from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import Group

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    must_change_password = models.BooleanField(default=False, help_text="Designates whether the user must change their password upon next login.")


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


    @property
    def role_label(self):
        """Return the human-readable label for the role integer."""
        return dict(self.ROLE_CHOICES).get(self.role)
    
    
    
    

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class RoleModulePermission(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    module = models.CharField(max_length=50)
    access_level = models.CharField(max_length=10, choices=[
        ('None', 'None'),
        ('View', 'View'),
        ('Edit', 'Edit'),
        ('Full', 'Full'),
    ])

    class Meta:
        unique_together = ('group', 'module')

    def __str__(self):
        return f"{self.group.name} - {self.module}: {self.access_level}"
    
    


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
