from django.urls import path
from .views import (
    DailyProductionRecordListCreateView, OperationListCreateView, OperationDetailView,
    MaintenanceListCreateView, MaintenanceDetailView,
    ProductionListCreateView, ProductionDetailView,
    OperationSummaryView, MaintenanceSummaryView,  
    DailyProductionRecordDetailView
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
    
    

# Add these to your urlpatterns list:
    path('daily/', DailyProductionRecordListCreateView.as_view(), name='daily-production-list'),
    path('daily/<int:id>/', DailyProductionRecordDetailView.as_view(), name='daily-production-detail'),

]