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

    # Role management
    RoleListView,
    RoleCreateView,

    # Auth
    SignupView,
    LoginView,
    RegisterView,
    CustomTokenObtainPairView,
)

from .views import (
    list_permissions_by_app,
    update_group_role,
    assign_role_to_user,
    update_roles_permissions,
    get_users_by_role,
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

    # Auth endpoints
    path('signup/', SignupView.as_view(), name='signup'),   # legacy signup
    path('login/', LoginView.as_view(), name='login'),     # legacy login
    path('register/', RegisterView.as_view(), name='register'),  # new registration
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWT login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Admin role-based permission endpoints
    path('permissions/<str:app_label>/', list_permissions_by_app, name='permissions-by-app'),
    path('roles/<int:id>/update/', update_group_role, name='update-role'),
    path('roles-permissions/', update_roles_permissions, name='update-roles-permissions'),
    path('<int:id>/assign-role/', assign_role_to_user, name='assign-role'),

    # Returns all users assigned to a specific role
    path('roles/<str:role_name>/users/', get_users_by_role, name='users-by-role'),
]
