from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter


from safety.views import SafetyIncidentViewSet

router = DefaultRouter()
router.register(r'safety-incidents', SafetyIncidentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
