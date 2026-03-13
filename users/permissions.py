from rest_framework.permissions import BasePermission

class IsSafetyOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 1 or request.user.is_superuser
        )

class IsInventoryManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 2 or request.user.is_superuser
        )

class IsProductionManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 3 or request.user.is_superuser
        )

class IsEquipmentManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 4 or request.user.is_superuser
        )
class IsProjectManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 0 or request.user.is_superuser
        )