from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('profile/<int:user_id>/', views.profile, name='public_profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.change_password, name='change_password'),
    path('player-stats/', views.player_stats, name='player_stats'),
    path('check-username/', views.check_username, name='check_username'),
]
