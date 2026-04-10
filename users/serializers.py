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
# Permission Serializer (Requirement 3: Explicit Codenames)
# ────────────────────────────────────────────────────────────────

class PermissionSerializer(serializers.ModelSerializer):
    """
    Returns permission details. The 'codename' field is critical for 
    the frontend to decide visibility (e.g., 'add_project', 'view_inventory').
    """
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name']


# ────────────────────────────────────────────────────────────────
# User Serializer (Requirement 1: Accurate User Object)
# ────────────────────────────────────────────────────────────────

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    role_label = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone_number', 'role', 'role_label', 
            'department', 'is_active', 'created_at', 'password', 
            'must_change_password', 'profile_image'
        ]
        read_only_fields = ['is_active', 'created_at', 'must_change_password']

    def get_role_label(self, obj):
        """Maps the integer role to its human-readable string."""
        if obj.role is not None:
            return dict(CustomUser.ROLE_CHOICES).get(obj.role)
        return "No Role Assigned"

    def validate_email(self, value):
        """Ensure email uniqueness during creation."""
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
            # For admin-created users without an initial password
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

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'phone_number', 'department', 'role', 'password']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.must_change_password = False
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customizes the JWT response to include the User object with 
    integer role IDs for immediate frontend UI updates.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # self.user is provided by the parent validate method
        user = self.user 
        
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,  # The Integer ID (0, 1, 2, 3, or 4)
            "role_label": dict(CustomUser.ROLE_CHOICES).get(user.role, "Unknown")
        }
        return data


# ────────────────────────────────────────────────────────────────
# Employee Serializer
# ────────────────────────────────────────────────────────────────

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'