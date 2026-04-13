import string
import secrets
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Permission
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# Import your custom models
from .models import CustomUser, Employee, RoleModulePermission

User = get_user_model()

# ────────────────────────────────────────────────────────────────
# Role Permission Serializer (New: For the "Feed")
# ────────────────────────────────────────────────────────────────

class RolePermissionSerializer(serializers.ModelSerializer):
    """Returns module-specific access levels for a role."""
    class Meta:
        model = RoleModulePermission
        fields = ['module', 'access_level']


# ────────────────────────────────────────────────────────────────
# User Serializer (Requirement 1: Accurate User Object)
# ────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    role_label = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField() # 👈 Added permissions feed

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone_number', 'role', 'role_label', 
            'department', 'is_active', 'is_superuser', 'is_staff', # 👈 Added superuser/staff
            'created_at', 'password', 'must_change_password', 
            'profile_image', 'permissions' # 👈 Added permissions to fields
        ]
        read_only_fields = ['is_active', 'created_at', 'must_change_password']

    def get_role_label(self, obj):
        """Maps the integer role to its human-readable string."""
        if obj.role is not None:
            return dict(CustomUser.ROLE_CHOICES).get(obj.role)
        return "No Role Assigned"

    def get_permissions(self, obj):
        """Feeds the list of module permissions tied to the user's role integer."""
        perms = RoleModulePermission.objects.filter(role_id=obj.role)
        return RolePermissionSerializer(perms, many=True).data

    def validate_email(self, value):
        if self.instance is None and CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
            user.must_change_password = False
        else:
            user.set_unusable_password()
            user.must_change_password = True
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
            instance.must_change_password = False
        instance.save()
        return instance


# ────────────────────────────────────────────────────────────────
# Auth & Token Serializers (Requirement 1: Dynamic Role mapping)
# ────────────────────────────────────────────────────────────────

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT response to include the full User object.
    This ensures Na'thanuel gets the superuser flag immediately on login.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user 
        
        # We fetch permissions here too for the immediate login response
        perms = RoleModulePermission.objects.filter(role_id=user.role)
        permissions_data = RolePermissionSerializer(perms, many=True).data

        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "role_label": dict(CustomUser.ROLE_CHOICES).get(user.role, "Unknown"),
            "is_superuser": user.is_superuser, # 👈 Critical for his frontend
            "is_staff": user.is_staff,
            "permissions": permissions_data # 👈 The "Everything" feed
        }
        return data