from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from users.views import SignupView, LoginView
from dashboard.views import DashboardSummary

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from accounts.views import CustomTokenObtainPairView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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

urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth endpoints
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # JWT endpoints
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('accounts.urls')),

    # API routes
    path('api/users/', include('users.urls')),
    path('api/safety/', include('safety.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/equipment/', include('equipment.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/dashboard/', include('dashboard.urls')),
    path('api/categories/', include(('category.urls', 'category'), namespace='category')),

    # Dashboard summary
    path('api/summary/', DashboardSummary.as_view()),
    
    
    # Production app routes 
    path('', include('production.urls')), # ✅ add this line
]

# 🖼️ Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
