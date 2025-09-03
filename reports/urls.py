from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet  # Make sure this class exists in views.py

router = DefaultRouter()
router.register(r'reports', ReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
