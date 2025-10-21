from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_list, name='highlights'),
    path('<slug:slug>/', views.news_detail, name='highlights_detail'),
]
