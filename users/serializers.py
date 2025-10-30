import string
import secrets
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, CustomUser

User = get_user_model()

# Utility function for secure password generation
def generate_random_password(length=12):
    """Generates a secure, random password."""
    characters = string.ascii_letters + string.digits + '@$!%*?&'
    return ''.join(secrets.choice(characters) for i in range(length))

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone_number', 'role', 'department',
            'is_active', 'created_at', 'password', 'must_change_password',
            'profile_image'  # 🖼️ New field added here
        ]
        read_only_fields = ['is_active', 'created_at', 'must_change_password']

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        temp_password = generate_random_password()
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=temp_password,
            must_change_password=True,
            **validated_data
        )

        user.temp_password_for_email = temp_password
        return user

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']

from django.contrib.auth.models import Permission, Group

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'content_type']

class GroupRoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']
