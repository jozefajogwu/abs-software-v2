from django.urls import path
from .views import (
    EquipmentListCreateView,
    EquipmentUpdateView,
    EquipmentDeleteView,
    EquipmentDetailView,
    EquipmentStatsView,
)

urlpatterns = [
    path('', EquipmentListCreateView.as_view(), name='equipment-list-create'),
    path('<int:id>/', EquipmentDetailView.as_view(), name='equipment-detail'),
    path('<int:id>/update/', EquipmentUpdateView.as_view(), name='equipment-update'),
    path('<int:id>/delete/', EquipmentDeleteView.as_view(), name='equipment-delete'),
    path('stats/', EquipmentStatsView.as_view(), name='equipment-stats'),
]
