from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='users-profile'),
    path('announcements/', views.announcements, name='users-announcements'),
    path('settings/', views.settings, name='users-settings'),
]
