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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),  # 👈 this sets up your homepage
    path('signup/', signup, name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('api/', include('safety.urls')),  # ← this wires in the safety app
    path('api/', include('reports.urls')),  # ← this wires in the reports app
    path('api/', include('users.urls')),  # ← this wires in the users app
    path('api/', include('projects.urls')),  # ← this wires in the projects app
    path('api/', include('equipment.urls')),  # ← this wires in the equipment app
    path("mfa/", mfa_method, name="mfa_method"),
    path("verify/", verify_mfa, name="verify_mfa"),
    # You can add more paths here later
]



