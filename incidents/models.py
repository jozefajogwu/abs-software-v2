from django.db import models

class Incident(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    reported_at = models.DateTimeField(auto_now_add=True)
    site = models.CharField(max_length=100)
 
