from django.urls import path
from .views import (
    OperationListCreateView, OperationDetailView,
    MaintenanceListCreateView, MaintenanceDetailView,
    ProductionListCreateView, ProductionDetailView,
    OperationSummaryView, MaintenanceSummaryView
)

urlpatterns = [
    # Operation
    path('operations/', OperationListCreateView.as_view(), name='operation-list-create'),
    path('operations/<int:id>/', OperationDetailView.as_view(), name='operation-detail'),
    path('operations/summary/', OperationSummaryView.as_view(), name='operation-summary'),

    # Maintenance
    path('maintenance/', MaintenanceListCreateView.as_view(), name='maintenance-list-create'),
    path('maintenance/<int:id>/', MaintenanceDetailView.as_view(), name='maintenance-detail'),
    path('maintenance/summary/', MaintenanceSummaryView.as_view(), name='maintenance-summary'),

    # Production
    path('records/', ProductionListCreateView.as_view(), name='production-list-create'),
    path('records/<int:id>/', ProductionDetailView.as_view(), name='production-detail'),
]