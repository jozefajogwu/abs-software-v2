from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import (
    UserViewSet,
    get_current_user,
    list_roles,
    create_role,
    activate_user,
    create_user,
    list_users,
    get_user,
    update_user,
    delete_user,
    user_stats
)

# ────────────────────────────────────────────────────────────────
# DRF Router for ViewSet (handles /api/users/)
# ────────────────────────────────────────────────────────────────

router = DefaultRouter()
router.register(r'', UserViewSet)  # Handles /api/users/

# ────────────────────────────────────────────────────────────────
# URL Patterns
# ────────────────────────────────────────────────────────────────

urlpatterns = [
    # DRF ViewSet routes
    path('', include(router.urls)),

    # JWT Authentication
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Current user info
    path('me/', get_current_user, name='get-current-user'),

    # Role management
    path('roles/', list_roles, name='list-roles'),
    path('roles/create/', create_role, name='create-role'),

    # Custom user management under /api/users/manage/
    path('manage/', list_users, name='list-users'),
    path('manage/create/', create_user, name='create-user'),
    path('manage/<int:id>/', get_user, name='get-user'),
    path('manage/<int:id>/update/', update_user, name='update-user'),
    path('manage/<int:id>/delete/', delete_user, name='delete-user'),
    path('manage/stats/', user_stats, name='user-stats'),

    # Activation link
    path('activate/<uidb64>/<token>/', activate_user, name='activate-user'),
]
