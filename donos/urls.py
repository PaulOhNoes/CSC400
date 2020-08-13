from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', DriveListView.as_view(), name='donos-home'),
    path('drive/city/<str:username>/', CityDriveListView.as_view(), name='donos-home-city'),
    path('drive/state/<str:username>/', StateDriveListView.as_view(), name='donos-home-state'),
    path('drive/follow/<str:username>/', FollowDriveListView.as_view(), name='donos-home-follow'),
    path('drive/yours/<str:username>/', YoursDriveListView.as_view(), name='donos-home-yours'),
    path('about/', views.about, name='donos-about'),
    path('drive/<int:pk>/', DriveDetailView.as_view(), name='drive-detail'),
    path('drive/<int:pk>/update/', DriveUpdateView.as_view(), name='drive-update'),
    path('drive/<int:pk>/delete/', DriveDeleteView.as_view(), name='drive-delete'),
    path('drive/<int:pk>/follow/', views.follow, name='drive-follow'),
    path('drive/<int:pk>/unfollow/', views.unfollow, name='drive-unfollow'),
    path('drive/<int:pk>/donate/<int:fnum>/', views.donate, name='drive-donate'),
    path('drive/<int:pk>/donate/<int:dnum>/view/', views.donation_view, name='drive-donation-view'),
    path('drive/<int:pk>/donate/<int:dnum>/edit/', views.donation_edit, name='drive-donation-edit'),
    path('drive/<int:pk>/donations', views.donations, name='drive-donations'),
    path('drive/<int:pk>/notification_post/', views.notification_post, name='drive-notification-post'),
    path('drive/<int:pk>/<int:id>/notification_view/', views.notification_view, name='drive-notification-view'),
    path('drive/new/', DriveCreateView.as_view(), name='drive-create'),
    path('organization/new/', views.org_register, name='donos-new_organization'),
    path('organization/<int:pk>/', views.organization_view, name='donos-organization-view'),
    path('organization/settings/', views.org_settings, name='donos-organization-settings'),
    path('locations/list/', views.locations_list, name='locations-list'),
    path('locations/map/', views.locations_map, name='locations-map'),
]
