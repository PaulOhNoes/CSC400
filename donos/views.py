from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from .models import Drive, Notifications, Organization, Donation
from donos.models import User, UserDrives
from users.forms import OrganizationForm, OrganizationUpdateForm
from .forms import *
import requests
import os

# Create your views here.


class DriveListView(ListView):
    model = Drive
    template_name = 'donos/home.html'
    context_object_name = 'drives'
    # newest to oldest drives
    ordering = ['-start_date']
    paginate_by = 5


class CityDriveListView(ListView):
    model = Drive
    template_name = 'donos/city_drives.html'
    context_object_name = 'drives'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Drive.objects.filter(city=user.profile.city).filter(state=user.profile.state).order_by('-start_date')


class StateDriveListView(ListView):
    model = Drive
    template_name = 'donos/state_drives.html'
    context_object_name = 'drives'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Drive.objects.filter(state=user.profile.state).order_by('-start_date')


class FollowDriveListView(ListView):
    model = Drive
    template_name = 'donos/follow_drives.html'
    context_object_name = 'drives'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return user.profile.follows.all().order_by('-start_date')


class YoursDriveListView(ListView):
    model = Drive
    template_name = 'donos/yours_drives.html'
    context_object_name = 'drives'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return user.organization.drive_set.all().order_by('-start_date')


class DriveDetailView(DetailView):
    model = Drive

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(DriveDetailView, self).get_context_data(**kwargs)
        follows = False
        user = self.request.user
        id = self.kwargs.get('pk')

        # Checks if the user follows the drive
        if self.request.user.is_authenticated:
            if user.profile.follows.filter(id=id).first():
                follows = True

        drive = Drive.objects.get(id=id)
        notifications = Notifications.objects.filter(drive=drive).order_by('-date_posted')
        total_dono = drive.donation_set.filter(approved=True).count()

        context['follows'] = follows
        context['notifications'] = notifications
        context['total_dono'] = total_dono
        return context


class DriveCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Drive
    # fields = ['title', 'content', 'start_date', 'end_date', 'address', 'city', 'state', 'zipcode']
    form_class = DriveForm

    # setting the Drive author and org
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.orgID = self.request.user.organization
        obj = form.save(commit=True)
        for category in form.cleaned_data['categories']:
            obj.category.add(category)
        obj.save()
        return super().form_valid(form)

    # checks if user is part of an organization and verified before creating a drive
    def test_func(self):
        try:
            if self.request.user.organization and self.request.user.organization.verified is True:
                return True
        except ObjectDoesNotExist:
            return False


class DriveUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Drive
    template_name = 'donos/drive_form.html'
    fields = ['title', 'content', 'end_date', 'address', 'city', 'state', 'zipcode']

    def test_func(self):
        drive = self.get_object()
        if self.request.user == drive.author:
            return True


class DriveDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Drive
    success_url = '/donos/'

    def test_func(self):
        drive = self.get_object()
        if self.request.user == drive.author:
            return True
        return False


def about(request):
    return render(request, 'donos/about.html')


@login_required()
def follow(request, pk):
    user = request.user
    drive = Drive.objects.get(id=pk)
    user.profile.follows.add(drive)
    messages.success(request, 'You have followed this drive!')
    return redirect('drive-detail', pk=pk)


@login_required()
def unfollow(request, pk):
    user = request.user
    a = user.profile.follows.filter(id=pk).first()
    # removes the relationship between the user.profile and drive
    user.profile.follows.remove(a)
    messages.success(request, 'You have unfollowed this drive!')
    return redirect('drive-detail', pk=pk)


@login_required()
def donate(request, pk, fnum):
    formset_base = formset_factory(DonationForm, extra=fnum)
    # WITHOUT form_kwargs CUSTOM PARAMETERS IN FORMS WOULD NOT WORK
    formset = formset_base(form_kwargs={'id': pk})
    helper = DonationFormSetHelper()
    if 'submit' in request.POST:
        formset = formset_base(request.POST, form_kwargs={'id': pk})
        if formset.is_valid():
            d = Donation.objects.create(drive=Drive.objects.get(id=pk), user=request.user, approved=False)
            d.save()
            d.refresh_from_db()
            for form in formset:
                obj = form.save(commit=False)
                obj.donation = d
                obj.save()
            return redirect('drive-detail', pk)
        else:
            messages.error(request, "Not valid!")
    elif 'form_add' in request.POST:
        fnum = fnum + 1
        return redirect('drive-donate', pk, fnum)
    elif 'form_remove' in request.POST:
        fnum = fnum - 1
        return redirect('drive-donate', pk, fnum)

    return render(request, 'donos/donate.html', {'formset': formset, 'helper': helper})


@login_required()
def donations(request, pk):
    donations = Drive.objects.get(pk=pk).donation_set.all().order_by('-date')
    author = Drive.objects.get(pk=pk).author

    if request.user != author:
        raise PermissionDenied()

    context = {'donations': donations}
    return render(request, 'donos/donations.html', context=context)


@login_required()
def donation_view(request, pk, dnum):
    # We use inlineformset_factory to retrieve instance data
    donation = Donation.objects.get(pk=dnum).donationitem_set.all()

    context = {
        'donation': donation,
    }
    return render(request, 'donos/donation_view.html', context)


@login_required()
def donation_edit(request, pk, dnum):
    # We use inlineformset_factory to retrieve instance data
    edit_form = inlineformset_factory(Donation, DonationItem, fields=('name', 'quantity', 'category'), extra=0)
    d = Donation.objects.get(pk=dnum)
    formset = edit_form(instance=d)

    if request.user != d.drive.author:
        raise PermissionDenied()

    if request.method == 'POST':
        formset = edit_form(request.POST, instance=d,)

        if formset.is_valid():
            formset.save()

            messages.success(request, f'Your donation has been updated!')
            d.approved = True
            d.save()
            return redirect('drive-detail', pk)
    return render(request, 'donos/donation_edit.html', {'formset': formset})



@login_required()
def notification_post(request, pk):
    drive = Drive.objects.get(id=pk)

    if request.user != drive.author:
        raise PermissionDenied()

    if request.method == 'POST':
        form = NotificationForm(request.POST)

        if form.is_valid():
            notif = form.save(commit=False)
            notif.drive = drive
            notif.save()
            messages.success(request, f'Your notification has been sent!')
            return redirect('drive-detail', pk=pk)
    else:
        form = NotificationForm()

    context = {'form': form}
    return render(request, 'donos/notification_post.html', context=context)


def notification_view(request, pk, id):
    data = Drive.objects.get(id=pk).notifications_set.get(pk=id)
    context = {'notification': data}
    return render(request, 'donos/notification_view.html', context=context)


def locations_list(request):
    list_results = []

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['search']

            text_query = 'charity OR food bank in {}'.format(data)
            text_query = text_query.replace(" ", "+")
            # fields: business_status, formatted_address, geometry[location][lat], geometry[location][lng], name,
            # opening_hours[open_now], user_ratings_total

            api_key = os.getenv('api_key')
            example = 'https://maps.googleapis.com/maps/api/place/textsearch/json?query={}&key={}'.format(text_query,
                                                                                                          api_key)

            response = requests.get(example)
            data = response.json()

            for x in range(len(data['results'])):
                list_results.append({'name': data['results'][x]['name'],
                                     'formatted_address': data['results'][x]['formatted_address'],
                                     'business_status': data['results'][x]['business_status'],
                                     'user_ratings_total': data['results'][x]['user_ratings_total'], })
                try:
                    list_results[x]['open'] = data['results'][x]['opening_hours']['open_now']
                except:
                    list_results[x]['open'] = None
    else:
        form = SearchForm()

    context = {'form': form,
               'list_results': list_results}
    return render(request, 'donos/locations_list.html', context=context)


def locations_map(request):
    link = None

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['search']
            text_query = 'charity OR food bank in {}'.format(data)
            text_query = text_query.replace(" ", "+")
            api_key = os.getenv('api_key')
            link = 'https://www.google.com/maps/embed/v1/search?key={}&q={}'.format(api_key, text_query)
    else:
        form = SearchForm()

    context = {
        'form': form,
        'link': link,
    }
    return render(request, 'donos/locations_map.html', context=context)


# org profile page
def organization_view(request, pk):
    org = Organization.objects.get(id=pk)
    drives = org.drive_set.all()
    context = {'org': org,
               'drives': drives}
    return render(request, 'donos/organization_view.html', context=context)


@login_required()
def org_register(request):
    if request.method == 'POST':
        form = OrganizationForm(request.POST, request.FILES)
        try:
            if form.is_valid:
                # commit=False tells Django that "Don't send this to database yet.
                # I have more things I want to do with it."

                org = form.save(commit=False)
                org.user = request.user
                # form.save()
                org.save()
                name = form.cleaned_data.get('name')
                messages.success(request, f'{name} Created!')
                return redirect('users-profile')
        except ValueError:
            messages.error(request, 'Validation form must be a pdf.')
            return redirect('donos-new_organization')
    else:
        form = OrganizationForm()

    context = {
        'form': form,
        'title': 'register',
    }
    return render(request, 'donos/register_org.html', context=context)


@login_required()
def org_settings(request):
    if request.method == 'POST':
        form = OrganizationUpdateForm(request.POST, request.FILES, instance=request.user.organization)

        if form.is_valid():
            form.save()

            messages.success(request, f'Your organization has been updated!')
            return redirect('donos-organization')
    else:
        form = OrganizationUpdateForm(instance=request.user.organization)

    context = {
        'form': form,
    }
    return render(request, 'donos/organization_settings.html', context=context)
