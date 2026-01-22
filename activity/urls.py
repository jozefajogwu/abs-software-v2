# activity/urls.py
from django.urls import path
from .views import RecentActivityView

urlpatterns = [
    path('recent/', RecentActivityView.as_view(), name='recent-activity'),
]
