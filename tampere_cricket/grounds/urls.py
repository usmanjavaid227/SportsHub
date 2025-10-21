from django.urls import path
from . import views

urlpatterns = [
    path('<int:ground_id>/', views.ground_detail, name='ground_detail'),
]
