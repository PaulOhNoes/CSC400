from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='users-profile'),
    path('announcements/drives/', views.announcements_drives, name='users-announcements-drives'),
    path('announcements/donations/', views.announcements_donations, name='users-announcements-donations'),
    path('settings/', views.settings, name='users-settings'),
]
