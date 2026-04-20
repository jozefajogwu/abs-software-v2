from .models import ActivityLog

def log_activity(user, app_name, model_name, object_id, action, description):
    """
    Logs user activity and automatically flags 'mutations' (Create/Update/Delete/Login)
    to keep the main dashboard feed clean as per Tuam's request.
    """
    # 1. Determine the Role Label for the description
    role = getattr(user, "role", None)
    # Safely get ROLE_CHOICES from the User model if it exists
    role_choices = getattr(user.__class__, "ROLE_CHOICES", [])
    role_label = dict(role_choices).get(role, "User")
    
    username = getattr(user, "username", "Anonymous")

    # 2. Define which actions count as 'mutations'
    # These are actions that change data or are critical for the main dashboard
    mutations = ['create', 'update', 'delete', 'login', 'unauthorized']
    is_mutation = action.lower() in mutations

    # 3. Create the log entry in the ActivityLog table
    ActivityLog.objects.create(
        user=user,
        app_name=app_name,
        model_name=model_name,
        object_id=object_id,
        action=action,
        is_mutation=is_mutation,
        description=f"{username} ({role_label}) — {description}"
    )