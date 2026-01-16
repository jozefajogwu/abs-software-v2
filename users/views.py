import random
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import Employee
from .serializers import EmployeeSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny

from django.contrib.auth.models import Permission, Group

from .models import CustomUser, RoleModulePermission
from .serializers import (
    UserSerializer,
    RoleSerializer,
    PermissionSerializer,
    GroupRoleSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
)
from users.utils import generate_activation_link, send_resend_email

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# ────────────────────────────────────────────────────────────────
# Auth views
# ────────────────────────────────────────────────────────────────

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Signup successful"}, status=status.HTTP_201_CREATED)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        identifier = request.data.get("username") or request.data.get("email")
        password = request.data.get("password")

        if not identifier or not password:
            return Response(
                {"detail": "Email/username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=identifier, password=password)
        if user:
            if getattr(user, "must_change_password", False):
                return Response(
                    {"detail": "Password change required", "must_change_password": True},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
            login(request, user)
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
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────────────────────
# User views
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

            try:
                send_activation_email(user)
            except Exception as e:
                print("Email error:", e)

            return Response(
                {"detail": "User created. Activation email sent.", "user": serializer.data},
                status=status.HTTP_201_CREATED,
            )

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
            return Response(serializer.data)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        user.delete()
        return Response({"detail": "User permanently deleted"}, status=status.HTTP_200_OK)


class UserStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total = CustomUser.objects.count()
        active = CustomUser.objects.filter(is_active=True).count()
        inactive = CustomUser.objects.filter(is_active=False).count()
        employees = CustomUser.objects.exclude(role__isnull=True).count()
        return Response(
            {
                "total_users": total,
                "active_users": active,
                "inactive_users": inactive,
                "employees": employees,
            },
            status=status.HTTP_200_OK,
        )


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": getattr(user, "role", "N/A"),
            },
            status=status.HTTP_200_OK,
        )


# ────────────────────────────────────────────────────────────────
# Role views
# ────────────────────────────────────────────────────────────────

class RoleListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        roles = [{"key": key, "label": label} for key, label in CustomUser._meta.get_field("role").choices]
        return Response(roles, status=status.HTTP_200_OK)


class RoleCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────────────────────
# Activation view
# ────────────────────────────────────────────────────────────────

class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"detail": "Invalid activation link"}, status=status.HTTP_400_BAD_REQUEST)

        if PasswordResetTokenGenerator().check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": "Account activated. Please set your password."}, status=status.HTTP_200_OK)
        return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────────────────────
# Utility
# ────────────────────────────────────────────────────────────────

def send_activation_email(user):
    activation_link = generate_activation_link(user)
    subject = "Activate Your ABV Account"
    html = f"""
        <p>Hello {user.username},</p>
        <p>Thanks for signing up! Click the link below to activate your account:</p>
        <p><a href="{activation_link}">Activate Account</a></p>
        <p>Once activated, you’ll be prompted to set your password.</p>
        <p>If you didn’t request this, you can safely ignore this email.</p>
    """
    send_resend_email(user.email, subject, html)


# ────────────────────────────────────────────────────────────────
# Permissions & role assignment views
# ────────────────────────────────────────────────────────────────

class ListPermissionsByAppView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, app_label):
        permissions_qs = Permission.objects.filter(content_type__app_label=app_label)
        serializer = PermissionSerializer(permissions_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateGroupRoleView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        group = get_object_or_404(Group, id=id)
        serializer = GroupRoleSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Role updated successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AssignRoleView(APIView):
    """
    Assign a role by updating CustomUser.role directly.
    Accepts either:
      { "role": "<role_key>" } OR { "role_id": <numeric_id> }
    """
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        user = get_object_or_404(User, id=id)

        role_id = request.data.get("role_id")

        
# ────────────────────────────────────────────────────────────────
# User creation with role assignment view
# ────────────────────────────────────────────────────────────────

class CreateUserWithRoleView(APIView):
    """
    Create a new user and assign a role in one request.
    Payload example:
    {
        "username": "joseph",
        "email": "joseph@example.com",
        "phone_number": "08012345678",
        "department": "IT",
        "password": "securepassword123",
        "role": 2   # Inventory Manager
    }
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        role_id = request.data.get("role")

        # ✅ Validate role against CustomUser.ROLE_CHOICES (integer IDs 0–4)
        valid_roles = dict(CustomUser.ROLE_CHOICES)
        if role_id not in valid_roles:
            return Response(
                {"detail": f"Invalid role_id '{role_id}'. Must be one of {list(valid_roles.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            # Save user with the validated role
            user = serializer.save(role=role_id)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UpdateRolesPermissionsView(APIView):
    """
    Update a user's role and/or permissions.
    Payload example:
    {
        "role": 2,                  # integer role ID
        "permissions": [1, 2, 3]    # list of permission IDs
    }
    """
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        user = get_object_or_404(CustomUser, id=id)

        role_id = request.data.get("role")
        permissions = request.data.get("permissions", [])

        # Validate role
        valid_roles = dict(CustomUser.ROLE_CHOICES)
        if role_id not in valid_roles:
            return Response({"detail": f"Invalid role_id '{role_id}'"}, status=status.HTTP_400_BAD_REQUEST)

        user.role = role_id

        # Assign permissions
        if permissions:
            perms_qs = Permission.objects.filter(id__in=permissions)
            user.user_permissions.set(perms_qs)

        user.save()
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)

class GetUsersByRoleView(APIView):
    """
    Return all users that have a given role.
    Example request: GET /api/users/by-role/?role=2
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        role_id = request.query_params.get("role")
        if role_id is None:
            return Response({"detail": "Missing role query parameter"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            role_id = int(role_id)
        except ValueError:
            return Response({"detail": "Role must be an integer"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate role against choices
        valid_roles = dict(CustomUser.ROLE_CHOICES)
        if role_id not in valid_roles:
            return Response({"detail": f"Invalid role_id '{role_id}'"}, status=status.HTTP_400_BAD_REQUEST)

        users = CustomUser.objects.filter(role=role_id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all().order_by('id')
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

