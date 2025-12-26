from django.urls import path
from .views import (
    # User management
    UserListCreateView,
    UserDetailView,
    UserUpdateView,
    UserDeleteView,
    UserStatsView,
    CurrentUserView,
    ActivateUserView,

    # Roles
    RoleListView,
    RoleCreateView,

    # Auth
    SignupView,
    LoginView,
    RegisterView,
    CustomTokenObtainPairView,
    LogoutView,

    # Permissions & role assignment
    ListPermissionsByAppView,
    UpdateGroupRoleView,
    AssignRoleView,
    UpdateRolesPermissionsView,
    GetUsersByRoleView,
)

from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # User endpoints
    path('', UserListCreateView.as_view(), name='user-list-create'),
    path('<int:id>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:id>/update/', UserUpdateView.as_view(), name='user-update'),
    path('<int:id>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('activate/<uidb64>/<token>/', ActivateUserView.as_view(), name='activate-user'),

    # Role endpoints
    path('roles/', RoleListView.as_view(), name='role-list'),
    path('roles/create/', RoleCreateView.as_view(), name='role-create'),
    path('roles/<str:role_name>/users/', GetUsersByRoleView.as_view(), name='users-by-role'),

    # Assign role directly via CustomUser.role
    path('<int:id>/assign-role/', AssignRoleView.as_view(), name='assign-role'),

    # Auth endpoints
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Permissions & group role management
    path('permissions/<str:app_label>/', ListPermissionsByAppView.as_view(), name='permissions-by-app'),
    path('roles/<int:id>/update/', UpdateGroupRoleView.as_view(), name='update-role'),
    path('roles-permissions/', UpdateRolesPermissionsView.as_view(), name='update-roles-permissions'),
]
