from django.urls import path
from . import views

app_name = 'admin_stats'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('player/<int:player_id>/', views.player_analysis, name='player_analysis'),
    path('comparison/', views.player_comparison, name='player_comparison'),
    path('ground/<int:ground_id>/', views.ground_analysis, name='ground_analysis'),
    path('records/', views.records, name='records'),
    path('api/statistics/', views.statistics_api, name='statistics_api'),
]
