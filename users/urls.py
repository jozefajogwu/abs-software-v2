from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    # User Management
    UserListCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    UserStatsView,
    CurrentUserView,
    ActivateUserView,
    CreateUserWithRoleView,

    # Roles & Assignment
    RoleListView,
    RoleCreateView,
    GetUsersByRoleView,
    AssignRoleView,
    
    # Auth
    SignupView,
    LoginView,
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,

    # Permissions Logic (The "Bridge" for the Frontend)
    ListPermissionsByAppView,
    UpdateGroupRoleView,  # Handles PUT /users/roles/${id}/update/
    UpdateRolesPermissionsView,
    
    # Employee
    EmployeeListCreateView, 
    EmployeeDetailView,
)

urlpatterns = [
    # ─── Auth Endpoints ──────────────────────────────────────────
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # ─── User Profile & Management ────────────────────────────────
    path('me/', CurrentUserView.as_view(), name='current-user'), # Requirement #1
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:id>/update/', UserUpdateView.as_view(), name='user-update'),
    path('<int:id>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate-user'),
    path('create-with-role/', CreateUserWithRoleView.as_view(), name='create-user-with-role'),

    # ─── Role & Permission Logic ──────────────────────────────────
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('roles/create/', RoleCreateView.as_view(), name='role-create'),
    path('roles/by-role/', GetUsersByRoleView.as_view(), name='users-by-role'),
    
    # This matches the frontend's Requirement #2 & #3
    path('roles/<int:id>/update/', UpdateGroupRoleView.as_view(), name='update-role'),
    path('permissions/<str:app_label>/', ListPermissionsByAppView.as_view(), name='permissions-by-app'),
    path('<int:id>/assign-role/', AssignRoleView.as_view(), name='assign-role'),
    path('roles-permissions/', UpdateRolesPermissionsView.as_view(), name='update-roles-permissions'),

    # ─── Employee Management ──────────────────────────────────────
    path('employees/', EmployeeListCreateView.as_view(), name='employee-list-create'),
    path('employees/<int:id>/', EmployeeDetailView.as_view(), name='employee-detail'),
]