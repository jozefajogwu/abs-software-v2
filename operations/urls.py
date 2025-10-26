from django.urls import path
from .views import (
    OperationListCreateView,
    OperationDetailView,
    OperationUpdateView,
    OperationDeleteView,
    OperationSummaryView,
    
    
    MaintenanceRecordListCreateView,
    MaintenanceRecordDetailView,
)

urlpatterns = [
    path('', OperationListCreateView.as_view(), name='operation-list-create'),
    path('<int:id>/', OperationDetailView.as_view(), name='operation-detail'),
    path('<int:id>/update/', OperationUpdateView.as_view(), name='operation-update'),
    path('<int:id>/delete/', OperationDeleteView.as_view(), name='operation-delete'),
    path('summary/', OperationSummaryView.as_view(), name='operation-summary'),
    
    path('maintenance/', MaintenanceRecordListCreateView.as_view(), name='maintenance-list-create'),
    path('maintenance/<int:id>/', MaintenanceRecordDetailView.as_view(), name='maintenance-detail'),
]

