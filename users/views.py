from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from donos.models import Notifications, Donation
from itertools import chain

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            messages.success(request, f'Account created for {username}!')
            user = authenticate(username=username,password=password)
            login(request, user)
            return redirect('register2')
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
        'title': 'register',
    }
    return render(request, 'users/register.html', context=context)


@login_required
def register2(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Account Finished!')
            return redirect('users-profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'form': form,
        'title': 'register',
    }
    return render(request, 'users/register2.html', context=context)


@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def announcements_drives(request):
    user = request.user
    drives = user.profile.follows.all()

    # create an empty queryset
    q = Notifications.objects.none()

    # union multiple queries together
    for drive in drives:
        q = q.union(drive.notifications_set.all())

    context = {
        'data': q.order_by('-date_posted'),
    }
    return render(request, 'users/announcements_drives.html', context=context)


@login_required
def announcements_donations(request):
    user = request.user
    drives = user.profile.follows.all()

    data = user.donation_set.all().order_by('-date')

    context = {
        'data': data,
    }
    return render(request, 'users/announcements_donations.html', context=context)


@login_required
def settings(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.success(request, f'Your account has been updated!')
            return redirect('users-profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'users/settings.html', context=context)