from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        print("Email:", email)  # Shows the email received from Postman

        try:
            user_obj = User.objects.get(email=email)
            print("User found:", user_obj.username)  # Confirms the user exists
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials")

        user = authenticate(username=user_obj.username, password=password)
        print("Authenticated:", user)  # Shows whether authentication succeeded

        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials")

        # Pass username and password to super().validate()
        data = super().validate({
            "username": user_obj.username,
            "password": password
        })

        data["user"] = {
            "id": user.id,
            "name": getattr(user, "name", user.username),
            "email": user.email,
        }

        return data
