from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from activity.models import RecentActivity
from django.contrib.auth import get_user_model

User = get_user_model()

from projects.models import Project
from equipment.models import Equipment
from safety.models import SafetyIncident
from inventory.models import Inventory
from operations.models import OperationRecord, MaintenanceRecord


# --- PROJECTS ---
@receiver(post_save, sender=Project)
def log_project_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    RecentActivity.objects.create(
        user=getattr(instance, "owner", None),
        app_name="projects",
        model_name="Project",
        object_id=instance.id,
        action=action,
        description=f"{action.capitalize()} project {instance.name}"
    )

@receiver(post_delete, sender=Project)
def log_project_delete(sender, instance, **kwargs):
    RecentActivity.objects.create(
        user=getattr(instance, "owner", None),
        app_name="projects",
        model_name="Project",
        object_id=instance.id,
        action="delete",
        description=f"Deleted project {instance.name}"
    )


# --- EQUIPMENT ---
@receiver(post_save, sender=Equipment)
def log_equipment_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    RecentActivity.objects.create(
        user=getattr(instance, "assigned_to", None),
        app_name="equipment",
        model_name="Equipment",
        object_id=instance.id,
        action=action,
        description=f"{action.capitalize()} equipment {instance.name}"
    )

@receiver(post_delete, sender=Equipment)
def log_equipment_delete(sender, instance, **kwargs):
    RecentActivity.objects.create(
        user=getattr(instance, "assigned_to", None),
        app_name="equipment",
        model_name="Equipment",
        object_id=instance.id,
        action="delete",
        description=f"Deleted equipment {instance.name}"
    )


# --- SAFETY INCIDENTS ---
@receiver(post_save, sender=SafetyIncident)
def log_incident_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    RecentActivity.objects.create(
        user=getattr(instance, "reported_by", None),
        app_name="safety",
        model_name="SafetyIncident",
        object_id=instance.id,
        action=action,
        description=f"{action.capitalize()} incident {instance.title}"
    )

@receiver(post_delete, sender=SafetyIncident)
def log_incident_delete(sender, instance, **kwargs):
    RecentActivity.objects.create(
        user=getattr(instance, "reported_by", None),
        app_name="safety",
        model_name="SafetyIncident",
        object_id=instance.id,
        action="delete",
        description=f"Deleted incident {instance.title}"
    )


# --- INVENTORY ---
@receiver(post_save, sender=Inventory)
def log_inventory_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    RecentActivity.objects.create(
        user=getattr(instance, "updated_by", None),
        app_name="inventory",
        model_name="Inventory",
        object_id=instance.id,
        action=action,
        description=f"{action.capitalize()} inventory item {instance.name}"
    )

@receiver(post_delete, sender=Inventory)
def log_inventory_delete(sender, instance, **kwargs):
    RecentActivity.objects.create(
        user=getattr(instance, "updated_by", None),
        app_name="inventory",
        model_name="Inventory",
        object_id=instance.id,
        action="delete",
        description=f"Deleted inventory item {instance.name}"
    )


# --- OPERATIONS ---
@receiver(post_save, sender=OperationRecord)
def log_operation_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    RecentActivity.objects.create(
        user=getattr(instance, "performed_by", None),
        app_name="operations",
        model_name="OperationRecord",
        object_id=instance.id,
        action=action,
        description=f"{action.capitalize()} operation record {instance.id}"
    )

@receiver(post_delete, sender=OperationRecord)
def log_operation_delete(sender, instance, **kwargs):
    RecentActivity.objects.create(
        user=getattr(instance, "performed_by", None),
        app_name="operations",
        model_name="OperationRecord",
        object_id=instance.id,
        action="delete",
        description=f"Deleted operation record {instance.id}"
    )


@receiver(post_save, sender=MaintenanceRecord)
def log_maintenance_save(sender, instance, created, **kwargs):
    action = "create" if created else "update"
    RecentActivity.objects.create(
        user=getattr(instance, "performed_by", None),
        app_name="operations",
        model_name="MaintenanceRecord",
        object_id=instance.id,
        action=action,
        description=f"{action.capitalize()} maintenance record {instance.id}"
    )

@receiver(post_delete, sender=MaintenanceRecord)
def log_maintenance_delete(sender, instance, **kwargs):
    RecentActivity.objects.create(
        user=getattr(instance, "performed_by", None),
        app_name="operations",
        model_name="MaintenanceRecord",
        object_id=instance.id,
        action="delete",
        description=f"Deleted maintenance record {instance.id}"
    )
