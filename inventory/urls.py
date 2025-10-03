from django.urls import path
from .views import (
    InventoryListCreateView,
    InventoryDetailView,
    InventorySummaryView
)

urlpatterns = [
    path('', InventoryListCreateView.as_view(), name='inventory-list-create'),
    path('<int:id>/', InventoryDetailView.as_view(), name='inventory-detail'),
    path('summary/', InventorySummaryView.as_view(), name='inventory-summary'),
]
