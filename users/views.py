from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from donos.models import Notifications, Donation, Drive
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
    user = request.user
    donations = user.donation_set.count()
    donations_approved = user.donation_set.filter(approved=True).count()
    fav = user.donation_set.all().values('drive').annotate(total=Count('drive')).order_by('-total').first()

    fav_drive = None
    fav_total = None

    # checks if user has donated
    if fav is not None:
        fav_drive = Drive.objects.get(pk=fav['drive'])
        fav_total = fav['total']

    context = {
        'donations': donations,
        'donations_approved': donations_approved,
        'fav_drive': fav_drive,
        'fav_drive_donations': fav_total,
    }
    return render(request, 'users/profile.html', context=context)


@login_required
def announcements_drives(request):
    user = request.user
    drives = user.profile.follows.all()

    page = request.GET.get('page')

    # create an empty queryset
    q = Notifications.objects.none()

    # union multiple queries together
    for drive in drives:
        q = q.union(drive.notifications_set.all())

    q = Paginator(q.order_by('-date_posted'), 5)
    context = {
        'data': q.get_page(page),
    }
    return render(request, 'users/announcements_drives.html', context=context)


@login_required
def announcements_donations(request):
    user = request.user

    page = request.GET.get('page')

    data = Paginator(user.donation_set.all().order_by('-date'),5)

    context = {
        'data': data.get_page(page),
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