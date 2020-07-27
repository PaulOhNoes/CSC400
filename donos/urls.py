from django.urls import path
from .views import DriveListView, DriveDetailView, DriveCreateView, DriveDeleteView, DriveUpdateView,\
    CityDriveListView, StateDriveListView
from . import views

urlpatterns = [
    path('', DriveListView.as_view(), name='donos-home'),
    path('drive/city/<str:username>', CityDriveListView.as_view(), name='donos-home-city'),
    path('drive/state/<str:username>', StateDriveListView.as_view(), name='donos-home-state'),
    path('about/', views.about, name='donos-about'),
    path('drive/<int:pk>/', DriveDetailView.as_view(), name='drive-detail'),
    path('drive/<int:pk>/update/', DriveUpdateView.as_view(), name='drive-update'),
    path('drive/<int:pk>/delete/', DriveDeleteView.as_view(), name='drive-delete'),
    path('drive/new/', DriveCreateView.as_view(), name='drive-create'),
    path('organization/new/', views.org_register, name='donos-new_organization'),
    path('organization/', views.organization, name='donos-organization'),
    path('organization/create_announcement/', views.create_announcement, name='create-announcement'),
    path('locations/list', views.locations_list, name='locations-list'),
    path('locations/map', views.locations_map, name='locations-map'),
]
