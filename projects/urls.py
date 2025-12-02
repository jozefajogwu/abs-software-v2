from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, AssignUsersToProjectView, ProjectStatsView

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('<int:pk>/assign-users/', AssignUsersToProjectView.as_view(), name='assign-users'),
    path('stats/', ProjectStatsView.as_view(), name='project-stats'),
]
