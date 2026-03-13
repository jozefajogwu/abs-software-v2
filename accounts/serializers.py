from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # We define these to tell the serializer to accept them from the JSON body
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        # 1. Manual authentication to verify the user exists and is active
        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError("No active account found with these credentials")

        # 2. Sync attrs with what the parent SimpleJWT class expects
        # SimpleJWT uses 'username' as the internal key regardless of your model field name
        attrs["username"] = email 
        
        # 3. Call parent validate to generate tokens (access & refresh)
        # This handles the token creation logic for us
        data = super().validate(attrs)
        
        # 4. Inject your custom user data into the final JSON response
        data["user"] = {
            "id": user.id,
            "name": getattr(user, "name", user.username),
            "email": user.email,
            "role": getattr(user, "role", "N/A")
        }
        return data