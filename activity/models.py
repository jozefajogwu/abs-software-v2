from django.db import models
from django.conf import settings

class RecentActivity(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),          # add this for read-only actions
        ('login', 'Logged In'),      # useful for tracking authentication
    ]

    app_name = models.CharField(max_length=50)              # e.g. "projects"
    model_name = models.CharField(max_length=50)            # e.g. "Project"
    object_id = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activities"   # makes reverse lookups easier
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)              # allow empty descriptions
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Recent Activity"
        verbose_name_plural = "Recent Activities"

    def __str__(self):
        return f"{self.user} {self.get_action_display()} {self.model_name} ({self.object_id})"
