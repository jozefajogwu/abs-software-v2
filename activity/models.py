from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('login', 'Logged In'),
        ('unauthorized', 'Unauthorized Access'), # Added for security auditing
    ]

    app_name = models.CharField(max_length=50)
    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="activities"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    
    # ✅ Tuam's Request: Flag for Mutations (Create/Update/Delete/Login)
    is_mutation = models.BooleanField(
        default=False, 
        help_text="True if this action changed data or state (Create/Update/Delete/Login)."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        user_display = self.user.username if self.user else "System/Anonymous"
        return f"{user_display} {self.get_action_display()} {self.model_name} ({self.object_id})"