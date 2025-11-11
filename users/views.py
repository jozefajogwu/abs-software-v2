import random
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import get_object_or_404

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

from django.contrib.auth.models import Permission, Group
from rest_framework.permissions import AllowAny

from .models import CustomUser, RoleModulePermission
from .serializers import (
    UserSerializer,
    RoleSerializer,
    PermissionSerializer,
    GroupRoleSerializer
)
from users.utils import generate_activation_link, send_resend_email

User = get_user_model()

# ────────────────────────────────────────────────────────────────
# Auth Views
# ────────────────────────────────────────────────────────────────

class SignupView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Signup successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")  # this is actually the email
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            if user.must_change_password:
                return Response({
                    "error": "Password change required.",
                    "must_change_password": True
                }, status=status.HTTP_401_UNAUTHORIZED)

            login(request, user)
            return Response({"message": "Login successful"})

        return Response({"error": "Invalid credentials"}, status=400)

# ────────────────────────────────────────────────────────────────
# User Views
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
            user.set_unusable_password()  # Prevent login until password is set
            user.save()

            try:
                send_activation_email(user)
            except Exception as e:
                print("Email error:", e)

            return Response({
                "message": "User created. Activation email sent.",
                "user": serializer.data
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserUpdateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def put(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, id):
        try:
            user = CustomUser.objects.get(id=id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        user.delete()
        return Response({"detail": "User permanently deleted"})


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
            "employees": employees
        })


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": getattr(user, 'role', 'N/A')
        })

# ────────────────────────────────────────────────────────────────
# Role Views
# ────────────────────────────────────────────────────────────────

class RoleListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        roles = [
            {"key": key, "label": label}
            for key, label in CustomUser._meta.get_field('role').choices
        ]
        return Response(roles)


class RoleCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ────────────────────────────────────────────────────────────────
# Activation View
# ────────────────────────────────────────────────────────────────

class ActivateUserView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            return Response({"detail": "Invalid activation link"}, status=400)

        if PasswordResetTokenGenerator().check_token(user, token):
            user.is_active = True
            user.save()
            return Response({"detail": "Account activated. Please set your password."})
        return Response({"detail": "Invalid or expired token"}, status=400)

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
# Permissions & Group Role Views
# ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_permissions_by_app(request, app_label):
    permissions = Permission.objects.filter(content_type__app_label=app_label)
    serializer = PermissionSerializer(permissions, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_group_role(request, id):
    group = get_object_or_404(Group, id=id)
    serializer = GroupRoleSerializer(group, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Role updated successfully'})
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def assign_role_to_user(request, id):
    user = get_object_or_404(User, id=id)
    role_id = request.data.get('role_id')

    if not role_id:
        return Response({"error": "Missing role_id"}, status=400)

    group = get_object_or_404(Group, id=role_id)
    user.groups.clear()
    user.groups.add(group)
    return Response({"message": f"Role '{group.name}' assigned to user '{user.username}'"})


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_roles_permissions(request):
    for role_data in request.data['roles']:
        role, _ = Group.objects.get_or_create(name=role_data['name'])
        for module, level in role_data['permissions'].items():
            RoleModulePermission.objects.update_or_create(
                group=role,
                module=module,
                defaults={"access_level": level}
            )
    return Response({"message": "Permissions updated successfully"})

# ────────────────────────────────────────────────────────────────
# Get Users by Role
# ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def get_users_by_role(request, role_name):
    users = CustomUser.objects.filter(role=role_name)
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

