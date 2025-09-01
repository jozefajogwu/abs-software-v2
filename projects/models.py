from users.models import CustomUser
from django.db import models
from django.conf import settings

# Create your models here.
class Project(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    assigned_projects = models.ManyToManyField('Project')
    project_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    assigned_team = models.TextField()  # List of team members (can be comma-separated)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    equipment = models.ManyToManyField('equipment.Equipment', related_name='projects', blank=True)
    inventory = models.ManyToManyField('inventory.Inventory', related_name='projects', blank=True)

    def __str__(self):
        return str(self.project_name)
    
   
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,  # ✅ allows existing rows to stay empty
    blank=True  # ✅ allows admin forms to skip it
    )
user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

