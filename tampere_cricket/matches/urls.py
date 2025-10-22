from django.urls import path
from . import views

urlpatterns = [
    path('', views.challenges_list, name='challenges_list'),
    path('create/', views.challenge_create, name='challenge_create'),
    path('create-edit/<int:challenge_id>/', views.challenge_create_edit, name='challenge_create_edit'),
    path('<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('<int:challenge_id>/edit/', views.challenge_edit, name='challenge_edit'),
    path('<int:challenge_id>/delete/', views.challenge_delete, name='challenge_delete'),
    path('<int:challenge_id>/accept/', views.challenge_accept, name='challenge_accept'),
    path('<int:challenge_id>/accept-direct/', views.open_challenge_accept, name='open_challenge_accept'),
    path('api/timeslots/', views.timeslots_api, name='timeslots_api'),
    # Admin views
    path('<int:challenge_id>/admin/update-result/', views.admin_update_match_result, name='admin_update_match_result'),
    path('<int:challenge_id>/admin/select-winner/', views.admin_select_winner, name='admin_select_winner'),
]
