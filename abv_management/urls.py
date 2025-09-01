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


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),  # 👈 this sets up your homepage
    path("login/", custom_login, name="login"),
     path("mfa/", mfa_method, name="mfa_method"),
     path("verify/", verify_mfa, name="verify_mfa"),
    # You can add more paths here later
]



