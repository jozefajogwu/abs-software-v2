from django.urls import path
from .views import (
    UserCategoryListCreateView,
    UserCategoryUpdateView,
    UserCategoryDeleteView
)

urlpatterns = [
    path('user-categories/', UserCategoryListCreateView.as_view(), name='user-category-list-create'),
    path('user-categories/<int:id>/', UserCategoryUpdateView.as_view(), name='user-category-update'),
    path('user-categories/<int:id>/delete/', UserCategoryDeleteView.as_view(), name='user-category-delete'),
    
]
