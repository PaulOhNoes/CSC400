from django.urls import path
from .views import DriveListView, DriveDetailView, DriveCreateView
from . import views

urlpatterns = [
    # path('', views.home, name='donos-home'),
    path('', DriveListView.as_view(), name='donos-home'),
    path('about/', views.about, name='donos-about'),
    # path('drive/view/', views.view_drive, name='drive-view'),
    path('drive/<int:pk>/', DriveDetailView.as_view(), name='drive-detail'),
    # path('drive/create/', views.create_drive, name='drive-create'),
    path('drive/new/', DriveCreateView.as_view(), name='drive-create'),
    path('organization/new/', views.org_register, name='donos-new_organization'),
    path('organization/', views.organization, name='donos-organization'),
    path('organization/create_announcement/', views.create_announcement, name='create-announcement'),
    path('locations/list', views.locations_list, name='locations-list'),
    path('locations/map', views.locations_map, name='locations-map'),
]
