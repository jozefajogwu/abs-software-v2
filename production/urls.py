from django.urls import path
from .views import (
    OperationListCreateView, OperationDetailView,
    MaintenanceListCreateView, MaintenanceDetailView,
    ProductionListCreateView, ProductionDetailView,
    OperationSummaryView, MaintenanceSummaryView
)

urlpatterns = [
    # Operation
    path('api/operation/', OperationListCreateView.as_view(), name='operation-list-create'),
    path('api/operation/<int:id>/', OperationDetailView.as_view(), name='operation-detail'),
    path('api/operation/summary/', OperationSummaryView.as_view(), name='operation-summary'),

    # Maintenance
    path('api/maintenance/', MaintenanceListCreateView.as_view(), name='maintenance-list-create'),
    path('api/maintenance/<int:id>/', MaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('api/maintenance/summary/', MaintenanceSummaryView.as_view(), name='maintenance-summary'),

    # Production
    path('api/production/', ProductionListCreateView.as_view(), name='production-list-create'),
    path('api/production/<int:id>/', ProductionDetailView.as_view(), name='production-detail'),
]
