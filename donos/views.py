from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Drive

# Create your views here.


def home(request):
    context = {
        'drives': Drive.objects.all(),
        'title': 'Home',
    }
    return render(request, 'donos/home.html', context=context)


def about(request):
    return render(request, 'donos/about.html')


@login_required
def create_drive(requests):
    return render(requests, 'donos/create_drive.html')


def view_drive(requests):
    return render(requests, 'donos/view_drive.html')


def locations_list(requests):
    return render(requests, 'donos/locations_list.html')


def locations_map(requests):
    return render(requests, 'donos/locations_map.html')


def organization(requests):
    return render(requests, 'donos/organization.html')


@login_required
def create_announcement(requests):
    return render(requests, 'donos/create_announcement.html')