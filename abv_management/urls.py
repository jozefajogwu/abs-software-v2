"""
URL configuration for abv_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import custom_login, verify_mfa, mfa_method
from users.views import homepage  # ✅ or from whatever app your homepage view is in
from users.views import signup
from django.contrib.auth import views as auth_views
from users.views import CustomLoginView
from django.urls import path, include
from dashboard.views import DashboardSummary
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('signup/', signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # ✅ Scoped API routes
    path('api/safety/', include('safety.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/users/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/equipment/', include('equipment.urls')),
    path('api/inventory/', include('inventory.urls')),
# ✅ now cleanly scoped
    path('api/dashboard/', include('dashboard.urls')),
    path('api/categories/', include(('category.urls', 'category'), namespace='category')),
    path('api/auth/', include('accounts.urls')),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # MFA and summary
    path("mfa/", mfa_method, name="mfa_method"),
    path("verify/", verify_mfa, name="verify_mfa"),
    path('api/summary/', DashboardSummary.as_view()),
]






schema_view = get_schema_view(
    openapi.Info(
        title="ABV Management API",
        default_version='v1',
        description="API documentation for ABV Management system",
        contact=openapi.Contact(email="support@abv.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)
