from django.urls import path
from .views import DashboardSummary
from .views import OperationalSummary
from .views import MaintenanceSummary
from .views import RecentActivityFeed
from .views import FinancialSummary
from .views import InventoryStatus
from .views import TransactionListView



urlpatterns = [
    path('summary/', DashboardSummary.as_view(), name='dashboard-summary'),
    path('operations/summary/', OperationalSummary.as_view(), name='operations-summary'),
    path('maintenance/summary/', MaintenanceSummary.as_view(), name='maintenance-summary'),
    path('activity/recent/', RecentActivityFeed.as_view(), name='recent-activity'),
    path('finance/summary/', FinancialSummary.as_view(), name='finance-summary'),
   path('inventory/status/', InventoryStatus.as_view(), name='inventory-status'),
   path('transactions/', TransactionListView.as_view(), name='transaction-list'),
          ]