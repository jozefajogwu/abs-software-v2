from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

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
            "name": getattr(user, "name", user.username),
            "email": user.email,
        }
        return data
