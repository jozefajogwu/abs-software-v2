import string
import secrets
from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.models import Permission, Group
from .models import Role, CustomUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

# Utility function for secure password generation
def generate_random_password(length=12):
    """Generates a secure, random password."""
    characters = string.ascii_letters + string.digits + '@$!%*?&'
    return ''.join(secrets.choice(characters) for _ in range(length))


# 🔹 General User Serializer (for listing, updating, admin use)
from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    role_label = serializers.SerializerMethodField()  # ✅ Human-readable role label

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'phone_number', 'role', 'role_label', 'department',
            'is_active', 'created_at', 'password', 'must_change_password',
            'profile_image'
        ]
        read_only_fields = ['is_active', 'created_at', 'must_change_password']

    def get_role_label(self, obj):
        """Return the human-readable label for the integer role."""
        if obj.role is not None:
            choices = dict(CustomUser.ROLE_CHOICES)
            return choices.get(obj.role)
        return None

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


# 🔹 Registration Serializer (for /api/users/register/)
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


# 🔹 Role Serializer
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


# 🔹 Permission Serializer
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'codename', 'name', 'content_type']


# 🔹 Group Role Serializer
class GroupRoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all()
    )

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']


# 🔹 Custom Token Serializer (for /api/token/)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'  # use email instead of username

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid credentials")

        data = super().validate(attrs)
        data["user"] = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "role_label": dict(CustomUser._meta.get_field("role").choices).get(user.role, user.role)
        }
        return data
