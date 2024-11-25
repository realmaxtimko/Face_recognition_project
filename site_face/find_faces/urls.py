from django.urls import path
from . import views


urlpatterns = [
    path('', views.main, name='main'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('clear_session/', views.clear_session, name='clear_session'),
]
