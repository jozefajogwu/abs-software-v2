from .models import RecentActivity

def log_activity(user, app_name, model_name, object_id, action, description):
    role = getattr(user, "role", None)
    role_label = dict(getattr(user.__class__, "ROLE_CHOICES", {})).get(role, "User")
    username = user.username

    RecentActivity.objects.create(
        user=user,
        app_name=app_name,
        model_name=model_name,
        object_id=object_id,
        action=action,
        description=f"{username} ({role_label}) — {description}"
    )
