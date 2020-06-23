from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm

# Create your views here.


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
        'title': 'register',
    }
    return render(request, 'users/register.html', context=context)


@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def announcements(requests):
    return render(requests, 'users/announcements.html')


@login_required
def settings(requests):
    return render(requests, 'users/settings.html')