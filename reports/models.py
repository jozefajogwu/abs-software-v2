from django.db import models
from django.conf import settings
from users.models import CustomUser



# Create your models here.
class Report(models.Model):
    REPORT_TYPES = [
        ('Project', 'Project Report'),
        ('Safety', 'Safety Report'),
        ('Inventory', 'Inventory Report'),
    ]

    report_type = models.CharField(max_length=100, choices=REPORT_TYPES)
    report_date = models.DateField()
    report_data = models.TextField()  # Store the report's content/data
    generated_by = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    null=True,   # ✅ allows existing rows to stay empty
    blank=True,  # ✅ allows admin forms to skip it
    related_name='generated_reports'
)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.report_type} - {self.report_date}"
    
    