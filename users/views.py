import random
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser, AllowAny
from django.contrib.auth.models import Permission, Group

from .models import Employee, CustomUser, RoleModulePermission
from .serializers import (
    EmployeeSerializer,
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

from activity.utils import log_activity   # ✅ import logger

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
            log_activity(request.user, "users", "CustomUser", user.id, "create", f"Admin created user: {user.username}")
            try:
                send_activation_email(user)
            except Exception as e:
                print("Email error:", e)
            return Response({"detail": "User created. Activation email sent.", "user": serializer.data},
                            status=status.HTTP_201_CREATED)
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


class UserStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        total = CustomUser.objects.count()
        active = CustomUser.objects.filter(is_active=True).count()
        inactive = CustomUser.objects.filter(is_active=False).count()
        employees = CustomUser.objects.exclude(role__isnull=True).count()
        return Response({
            "total_users": total,
            "active_users": active,
            "inactive_users": inactive,
            "employees": employees,
        }, status=status.HTTP_200_OK)


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
# Role & Permission views
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
            role = serializer.save()
            log_activity(request.user, "users", "Role", role.id, "create", f"Created new role: {role.name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UpdateGroupRoleView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, id):
        group = get_object_or_404(Group, id=id)
        serializer = GroupRoleSerializer(group, data=request.data)
        if serializer.is_valid():
            serializer.save()
            log_activity(request.user, "users", "Group", group.id, "update", f"Updated group role: {group.name}")
            return Response({"detail": "Role updated successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AssignRoleView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        user = get_object_or_404(User, id=id)
        role_id = request.data.get("role_id")
        if role_id:
            user.role = role_id
            user.save()
            log_activity(request.user, "users", "CustomUser", user.id, "update", f"Assigned role {role_id} to user {user.username}")
            return Response({"detail": "Role assigned successfully"}, status=status.HTTP_200_OK)
        return Response({"detail": "Missing role_id"}, status=status.HTTP_400_BAD_REQUEST)


class UpdateRolesPermissionsView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        role_id = request.data.get("role")
        permissions_list = request.data.get("permissions", [])

        if role_id:
            user.role = role_id
        if permissions_list:
            perms_qs = Permission.objects.filter(id__in=permissions_list)
            user.user_permissions.set(perms_qs)
        user.save()

        log_activity(request.user, "users", "CustomUser", user.id, "update", f"Updated role/permissions for user {user.username}")
        return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


class GetUsersByRoleView(APIView):
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
            log_activity(user, "users", "CustomUser", user.id, "update", f"Activated user account: {user.username}")
            return Response({"detail": "Account activated. Please set your password."}, status=status.HTTP_200_OK)

        return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────────────────────
# Permissions & role assignment views
# ────────────────────────────────────────────────────────────────

class ListPermissionsByAppView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, app_label):
        permissions_qs = Permission.objects.filter(content_type__app_label=app_label)
        serializer = PermissionSerializer(permissions_qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateUserWithRoleView(APIView):
    """
    Create a new user and assign a role in one request.
    """
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        role_id = request.data.get("role")

        valid_roles = dict(CustomUser.ROLE_CHOICES)
        if role_id not in valid_roles:
            return Response(
                {"detail": f"Invalid role_id '{role_id}'. Must be one of {list(valid_roles.keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role=role_id)
            log_activity(request.user, "users", "CustomUser", user.id, "create",
                         f"Admin created user with role {valid_roles[role_id]}: {user.username}")
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ────────────────────────────────────────────────────────────────
# Employee views
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
