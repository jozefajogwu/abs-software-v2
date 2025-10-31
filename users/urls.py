from django.urls import path
from .views import list_permissions_by_app, update_group_role, assign_role_to_user
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

    # Auth & MFA
    SignupView,
    LoginView,
   
)

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

    # Auth & MFA endpoints
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    #path('mfa/', MfaMethodView.as_view(), name='mfa-method'),
    #path('verify/', VerifyMfaView.as_view(), name='verify-mfa'),
    
    
    
    #admin role based permission endpoints

    

    
    path('permissions/<str:app_label>/', list_permissions_by_app, name='permissions-by-app'),
    path('permissions/<str:app_label>/', list_permissions_by_app, name='permissions-by-app'),
    path('roles/<int:id>/update/', update_group_role, name='update-role'),
    # other endpoints...
    
    path('<int:id>/assign-role/', assign_role_to_user, name='assign-role'),

]

