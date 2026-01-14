from django.urls import path
from .views import (
    InventoryListCreateView,
    InventoryDetailView,
    InventorySummaryView
)

app_name = "inventory"  # 👈 namespace

urlpatterns = [
    path('items/', InventoryListCreateView.as_view(), name='items-list-create'),
    path('items/<int:id>/', InventoryDetailView.as_view(), name='items-detail'),
    path('summary/', InventorySummaryView.as_view(), name='summary'),
]
