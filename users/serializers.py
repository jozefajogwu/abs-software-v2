# users.serializers.py

import string
import secrets
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, CustomUser

User = get_user_model()


# Utility function for secure password generation
def generate_random_password(length=12):
    """Generates a secure, random password."""
    # Using letters, digits, and a few common symbols
    characters = string.ascii_letters + string.digits + '@$!%*?&'
    return ''.join(secrets.choice(characters) for i in range(length))

class UserSerializer(serializers.ModelSerializer):
    # Add password field only for write operations.
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        # Add 'must_change_password' to fields
        fields = ['id', 'username', 'email', 'phone_number', 'role', 'department', 
                  'is_active', 'created_at', 'password', 'must_change_password']
        # 'is_active', 'created_at', and the new flag are read-only
        read_only_fields = ['is_active', 'created_at', 'must_change_password'] 

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        # 1. Generate a temporary password
        temp_password = generate_random_password()
        
        # 2. Extract specific fields, falling back to None if not provided (though username should be provided)
        username = validated_data.pop('username', None)
        email = validated_data.pop('email', None)

        # 3. Create the user with the temporary password and forced change flag
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=temp_password, # Set the temporary password
            must_change_password=True, # Set the flag to force password change
            **validated_data # Pass remaining validated fields (role, department, phone_number, etc.)
        )
        
        # 4. Store the temporary password on the instance for the view to use in the email utility
        user.temp_password_for_email = temp_password
        
        return user

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']