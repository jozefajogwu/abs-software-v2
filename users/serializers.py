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
# Utility Utilities
# ────────────────────────────────────────────────────────────────

def generate_random_password(length=12):
    """Generates a secure, random password for admin-created users."""
    characters = string.ascii_letters + string.digits + '@$!%*?&'
    return ''.join(secrets.choice(characters) for _ in range(length))


# ────────────────────────────────────────────────────────────────
# Role & Permission Serializers
# ────────────────────────────────────────────────────────────────

class PermissionSerializer(serializers.ModelSerializer):
    """Returns basic Django permission details."""
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name']


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Returns module-specific access levels.
    Maps permission_id to 'permission' to match Na'thanuel's frontend payload.
    """
    permission = serializers.IntegerField(source='permission_id', allow_null=True)

    class Meta:
        model = RoleModulePermission
        fields = ['module', 'access_level', 'permission']


class RoleSerializer(serializers.Serializer):
    """
    Used for the GET /api/users/roles/ endpoint.
    Combines static ROLE_CHOICES with saved database permissions.
    """
    id = serializers.IntegerField()
    label = serializers.CharField()
    permissions = serializers.SerializerMethodField()

    def get_permissions(self, obj):
        # Handles both dicts (from views) and model instances
        role_id = obj.get('id') if isinstance(obj, dict) else obj.id
        perms = RoleModulePermission.objects.filter(role_id=role_id)
        return RolePermissionSerializer(perms, many=True).data


# ────────────────────────────────────────────────────────────────
# User Serializer (The "Main Feed")
# ────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    role_label = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone_number', 'role', 'role_label', 
            'department', 'is_active', 'is_superuser', 'is_staff', 
            'created_at', 'password', 'must_change_password', 
            'profile_image', 'permissions'
        ]
        read_only_fields = ['is_active', 'created_at', 'must_change_password']

    def get_role_label(self, obj):
        """Maps the integer role to its human-readable string."""
        if obj.role is not None:
            return dict(CustomUser.ROLE_CHOICES).get(obj.role)
        return "No Role Assigned"

    def get_permissions(self, obj):
        """Feeds the full list of permissions tied to the user's role integer."""
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
# Auth & Token Serializers
# ────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'department', 'role', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.must_change_password = False
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT response to include the full User object.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user 
        
        # Fetch permissions for the immediate login response
        perms = RoleModulePermission.objects.filter(role_id=user.role)
        permissions_data = RolePermissionSerializer(perms, many=True).data

        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "role_label": dict(CustomUser.ROLE_CHOICES).get(user.role, "Unknown"),
            "is_superuser": user.is_superuser,
            "is_staff": user.is_staff,
            "permissions": permissions_data
        }
        return data


# ────────────────────────────────────────────────────────────────
# Employee Serializer
# ────────────────────────────────────────────────────────────────

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'