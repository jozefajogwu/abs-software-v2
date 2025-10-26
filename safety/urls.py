from django.urls import path, include
from rest_framework.routers import DefaultRouter
from safety.views import SafetyIncidentViewSet, RiskAssessmentViewSet

router = DefaultRouter()
router.register(r'safety-incidents', SafetyIncidentViewSet)
router.register(r'risk-assessments', RiskAssessmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
