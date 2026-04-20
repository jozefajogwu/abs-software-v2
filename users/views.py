import random
from django.contrib.auth import authenticate, get_user_model, login
from django.db import transaction # ✅ Added for Supabase transaction stability
from django.shortcuts import get_object_or_404
from django.db.models import Count
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
    RoleSerializer,  # ✅ Added for role permission lookup
)
from users.utils import generate_activation_link, send_resend_email
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from activity.utils import log_activity

User = get_user_model()

# ─── AUTH VIEWS ────────────────────────────────────────────────

class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            log_activity(user, "users", "CustomUser", user.id, "create", f"Signed up: {user.username}")
            return Response({"detail": "Signup successful"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

# ─── USER MANAGEMENT VIEWS ────────────────────────────────────

class UserListCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def get(self, request):
        users = CustomUser.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    permission_classes = [permissions.IsAdminUser]
    def delete(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        user.delete()
        return Response({"detail": "Deleted"}, status=status.HTTP_200_OK)

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UserStatsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        role_counts = CustomUser.objects.values('role').annotate(count=Count('role'))
        role_labels = dict(CustomUser.ROLE_CHOICES)
        stats_by_role = {role_labels.get(item['role'], "N/A"): item['count'] for item in role_counts}
        return Response({
            "total_users": CustomUser.objects.count(),
            "by_role": stats_by_role
        })

class ActivateUserView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, uidb64, token):
        return Response({"detail": "Activation endpoint active"})

class CreateUserWithRoleView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

# ─── ROLE & PERMISSION LOGIC (REFACTORED) ──────────────────────

class RoleListView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        # ✅ Updated to use RoleSerializer to fetch saved permissions from the DB
        roles_data = [{"id": k, "label": v} for k, v in CustomUser.ROLE_CHOICES]
        serializer = RoleSerializer(roles_data, many=True)
        return Response(serializer.data)

class RoleCreateView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        return Response({"detail": "Role metadata created"})

class UserRoleView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        return Response({"role": user.role})

class AssignRoleView(APIView):
    permission_classes = [IsAdminUser]
    def put(self, request, id):
        user = get_object_or_404(CustomUser, id=id)
        role = request.data.get("role")
        with transaction.atomic(): # ✅ Ensure role save commits to Supabase
            user.role = int(role)
            user.save()
        log_activity(request.user, "users", "CustomUser", user.id, "update", f"Assigned role {role} to {user.username}")
        return Response({"detail": "Role assigned"})

class GetUsersByRoleView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        role = request.query_params.get("role")
        users = CustomUser.objects.filter(role=int(role))
        return Response(UserSerializer(users, many=True).data)

class ListPermissionsByAppView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, app_label):
        perms = Permission.objects.filter(content_type__app_label=app_label)
        return Response([{"id": p.id, "codename": p.codename, "name": p.name} for p in perms])

class UpdateRolePermissionsView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        role_id = int(id)
        # Na'thanuel is sending the array under the key "permissions"
        permissions_data = request.data.get("permissions", [])
        
        if not permissions_data:
            return Response({"detail": "No permissions provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():  # ✅ Ensures all 48 items save or none do
                for perm in permissions_data:
                    # We extract 'permission' from his JSON to use as our permission_id
                    p_id = perm.get('permission')
                    module_name = perm.get('module')
                    
                    RoleModulePermission.objects.update_or_create(
                        role_id=role_id, 
                        module=module_name,
                        permission_id=p_id, # 👈 Now distinct rows per permission ID
                        defaults={
                            'access_level': str(perm.get('access_level'))
                        }
                    )
            
            # Log the successful bulk update
            log_activity(
                request.user, 
                "users", 
                "RoleModulePermission", 
                None, 
                "update", 
                f"Updated {len(permissions_data)} permissions for Role ID {role_id}"
            )
            
            return Response({
                "detail": f"Successfully updated {len(permissions_data)} permissions"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
# ─── EMPLOYEE VIEWS ───────────────────────────────────────────

class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated]