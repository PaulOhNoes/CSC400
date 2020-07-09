from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Drive
from users.forms import OrganizationForm

# Create your views here.


# def home(request):
#     context = {
#         'drives': Drive.objects.all(),
#         'title': 'Home',
#     }
#     return render(request, 'donos/home.html', context=context)


class DriveListView(ListView):
    model = Drive
    template_name = 'donos/home.html'
    context_object_name = 'drives'
    # newest to oldest drives
    ordering = ['-start_date']


class DriveDetailView(DetailView):
    model = Drive


class DriveCreateView(CreateView):
    model = Drive
    fields = ['title', 'content']

    # setting the Drive author and org
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.orgID = self.request.user.organization
        return super().form_valid(form)


def about(request):
    return render(request, 'donos/about.html')


def locations_list(requests):
    return render(requests, 'donos/locations_list.html')


def locations_map(requests):
    return render(requests, 'donos/locations_map.html')


def organization(requests):
    return render(requests, 'donos/organization.html')


@login_required
def create_announcement(requests):
    return render(requests, 'donos/create_announcement.html')


@login_required()
def org_register(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid:
            # commit=False tells Django that "Don't send this to database yet.
            # I have more things I want to do with it."

            org = form.save(commit=False)
            org.user = request.user
            form.save()
            name = form.cleaned_data.get('name')
            messages.success(request, f'{name} Created!')
            return redirect('users-profile')
    else:
        form = OrganizationForm()

    context = {
        'form': form,
        'title': 'register',
    }
    return render(request, 'donos/register_org.html', context=context)