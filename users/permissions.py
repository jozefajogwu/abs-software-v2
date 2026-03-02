from rest_framework.permissions import BasePermission

class IsSafetyOfficer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "safety_officer"

class IsOperationsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "operations_manager"

class IsProjectManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "project_manager"

class IsEquipmentManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "equipment_manager"

class IsInventoryManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "inventory_manager"

class IsAccountsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "accounts_manager"

class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "superuser"
