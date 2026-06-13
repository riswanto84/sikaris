from django.urls import path
from .views import DashboardView, dashboard_stats_api

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('api/dashboard-stats/', dashboard_stats_api, name='dashboard_stats_api'),
]
