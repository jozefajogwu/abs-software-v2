import random
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from django.contrib.auth.models import Permission

from .models import Employee, CustomUser, RoleModulePermission
from .serializers import (
    EmployeeSerializer,
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from users.utils import generate_activation_link, send_resend_email
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from activity.utils import log_activity

User = get_user_model()

# ────────────────────────────────────────────────────────────────
# Auth views
# ────────────────────────────────────────────────────────────────

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            log_activity(user, "users", "CustomUser", user.id, "create", f"Signed up new user: {user.username}")
            return Response({"detail": "Signup successful"}, status=status.HTTP_201_CREATED)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=identifier, password=password)
        if user:
            login(request, user)
            log_activity(user, "users", "CustomUser", user.id, "login", f"User logged in: {user.username}")
            return Response({"detail": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            log_activity(request.user, "users", "CustomUser", request.user.id, "logout", f"User logged out: {request.user.username}")
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

# ────────────────────────────────────────────────────────────────
# User Management Views
# ────────────────────────────────────────────────────────────────

class UserListCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(is_active=False)
            user.set_unusable_password()
            user.save()
            log_activity(request.user, "users", "CustomUser", user.id, "create", f"Admin created user: {user.username}")
            return Response({"detail": "User created.", "user": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class UserUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def put(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            log_activity(request.user, "users", "CustomUser", user.id, "update", f"Admin updated user: {user.username}")
            return Response(serializer.data)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def delete(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        log_activity(request.user, "users", "CustomUser", user.id, "delete", f"Admin deleted user: {user.username}")
        user.delete()
        return Response({"detail": "User permanently deleted"}, status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": getattr(user, "role", "N/A"),
        }, status=status.HTTP_200_OK)

# ────────────────────────────────────────────────────────────────
# Role & Permission Logic (CLEAN INTEGER ID METHOD)
# ────────────────────────────────────────────────────────────────

class RoleListView(APIView):
    """
    Returns the list of integer-based roles. 
    Added 'id' field matching 'key' to satisfy frontend frameworks.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        roles = [
            {"id": key, "key": key, "label": label} 
            for key, label in CustomUser.ROLE_CHOICES
        ]
        return Response(roles, status=status.HTTP_200_OK)

class UpdateGroupRoleView(APIView):
    """
    REFACTORED: Handles integer role IDs instead of Group Primary Keys.
    This fixes the 'No Group matches' 404 error.
    """
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, id):
        # 'id' in the URL is now the role integer (0, 1, 2, 3, or 4)
        role_id = int(id)
        permissions_data = request.data.get("permissions", [])

        # We update our custom RoleModulePermission table
        for perm in permissions_data:
            RoleModulePermission.objects.update_or_create(
                role_id=role_id,  # Ensure your model has 'role_id' field
                module=perm.get('module'),
                defaults={'access_level': perm.get('access_level')}
            )
        
        log_activity(request.user, "users", "RoleModulePermission", role_id, "update", f"Updated permissions for integer role {role_id}")
        return Response({"detail": "Permissions updated successfully"}, status=status.HTTP_200_OK)

class AssignRoleView(APIView):
    """
    Assigns an integer role to a specific user.
    """
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        user = get_object_or_404(User, id=id)
        role_id = request.data.get("role")
        
        if role_id is not None:
            user.role = int(role_id)
            user.save()
            log_activity(request.user, "users", "CustomUser", user.id, "update", f"Assigned role {role_id} to {user.username}")
            return Response({"detail": "Role assigned successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "Missing role_id"}, status=status.HTTP_400_BAD_REQUEST)

class GetUsersByRoleView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        role_id = request.query_params.get("role")
        if role_id is None:
            return Response({"detail": "Missing role query parameter"}, status=status.HTTP_400_BAD_REQUEST)
        
        users = CustomUser.objects.filter(role=int(role_id))
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# ────────────────────────────────────────────────────────────────
# Employee Views
# ────────────────────────────────────────────────────────────────

class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        employee = serializer.save()
        log_activity(self.request.user, "users", "Employee", employee.id, "create", f"Added employee: {employee.name}")

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def perform_update(self, serializer):
        employee = serializer.save()
        log_activity(self.request.user, "users", "Employee", employee.id, "update", f"Updated employee: {employee.name}")

    def perform_destroy(self, instance):
        log_activity(self.request.user, "users", "Employee", instance.id, "delete", f"Deleted employee: {instance.name}")
        instance.delete()