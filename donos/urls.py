from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='donos-home'),
    path('about/', views.about, name='donos-about'),
    path('drive/view/', views.view_drive, name='drive-view'),
    path('drive/create/', views.create_drive, name='drive-create'),
    path('organization/', views.organization, name='organization'),
    path('organization/create_announcement/', views.create_announcement, name='create-announcement'),
    path('locations/list', views.locations_list, name='locations-list'),
    path('locations/map', views.locations_map, name='locations-map'),
]
