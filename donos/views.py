from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, request
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.urls import reverse
from django.forms import formset_factory, modelformset_factory, inlineformset_factory
from .models import *
from donos.models import *
from users.forms import OrganizationForm, OrganizationUpdateForm
from .forms import *
import requests
import os

# Create your views here.


def error_404(request, exception):
    data = {}
    return render(request, 'donos/404.html', data)


def error_403(request, exception):
    data = {}
    return render(request, 'donos/403.html', data)


class DriveListView(ListView):
    model = Drive
    template_name = 'donos/home.html'
    context_object_name = 'drives'
    paginate_by = 5

    def get_queryset(self):
        return Drive.objects.filter(end_date__gt=timezone.now()).order_by('-start_date')


class CityDriveListView(ListView):
    model = Drive
    template_name = 'donos/city_drives.html'
    context_object_name = 'drives'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Drive.objects.filter(end_date__gt=timezone.now())\
            .filter(city=user.profile.city)\
            .filter(state=user.profile.state)\
            .order_by('-start_date')


class StateDriveListView(ListView):
    model = Drive
    template_name = 'donos/state_drives.html'
    context_object_name = 'drives'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Drive.objects.filter(end_date__gt=timezone.now())\
            .filter(state=user.profile.state)\
            .order_by('-start_date')


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

        page = self.request.GET.get('page')

        follows = False
        user = self.request.user
        id = self.kwargs.get('pk')

        # Checks if the user follows the drive
        if self.request.user.is_authenticated:
            if user.profile.follows.filter(id=id).first():
                follows = True

        # drive notifications
        drive = Drive.objects.get(id=id)
        notifications = Paginator(Notifications.objects.filter(drive=drive).order_by('-date_posted'), 5)

        # drive stats
        total_dono = drive.donation_set.filter(approved=True).count()

        context['follows'] = follows
        context['notifications'] = notifications.get_page(page)
        context['total_dono'] = total_dono
        context['followers'] = drive.followed_by.count()
        return context


class DriveCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Drive
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
    fields = ['title', 'content', 'end_date', 'address', 'city', 'state', 'zipcode', 'progress', 'banner']

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
    page = request.GET.get('page')

    query = Drive.objects.get(pk=pk).donation_set.all()
    donations = Paginator(query.order_by('-date'), 10)
    author = Drive.objects.get(pk=pk).author

    if request.user != author:
        raise PermissionDenied()

    if request.method == 'POST':
        form = DonationSearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['search']
            return redirect('drive-donation-edit', pk, data)

    else:
        form = DonationSearchForm()

    context = {'donations': donations.get_page(page),
               'form': form, }
    return render(request, 'donos/donations.html', context=context)


@login_required()
def donation_view(request, pk, dnum):
    donation = Donation.objects.get(pk=dnum)
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

    # user must be the owner and using the respective drive
    if request.user != d.drive.author or pk != d.drive.id:
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
def drive_stats(request, pk):
    drive = Drive.objects.get(id=pk)

    if request.user != drive.author:
        raise PermissionDenied()

    # empty dictionary for categories count
    dict = {}

    # initialize values for dictionary
    for x in Category.objects.all():
        dict[x.name] = 0

    drives = Drive.objects.get(pk=pk).donation_set.all()

    # donations count
    total_dono = drive.donation_set.count()
    total_approved = drive.donation_set.filter(approved=True).count()
    total_unapproved = total_dono - total_approved

    donors = drive.donation_set.values('user').annotate(total=Count('user')).order_by('-total')[0:3]
    top_donors = []
    if donors is not None:
        for donor in donors:
            top_donors.append(User.objects.get(pk=donor['user']))

    # add approved items to dictionary count
    for drive in drives.all().filter(approved=True):
        dono = drive.donationitem_set.all()
        for item in dono:
            dict[item.category.name] = dict[item.category.name] + item.quantity

    drive = Drive.objects.get(id=pk)

    context = {'drive': drive,
               'dict': dict,
               'total_dono': total_dono,
               'total_approved': total_approved,
               'total_unapproved': total_unapproved,
               'top_donors': top_donors,
               'time_left': drive.time_left,
               'followers': drive.followed_by.count()
               }
    return render(request, 'donos/drive_stats.html', context=context)


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

                # Not all results have opening hours
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
    link = 'https://www.google.com/maps/embed/v1/search?key={}&q={}'
    api_key = os.getenv('api_key')

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data['search']
            text_query = 'charity OR food bank in {}'.format(data)
            text_query = text_query.replace(" ", "+")
            link = link.format(api_key, text_query)
    else:
        link = 'https://www.google.com/maps/embed/v1/search?key={}&q=charity+OR+food+bank+in+{}'.format(api_key, request.user.profile.zipcode)
        form = SearchForm()

    context = {
        'form': form,
        'link': link,
    }
    return render(request, 'donos/locations_map.html', context=context)


# org profile page
def organization_view(request, pk):
    page = request.GET.get('page')

    org = Organization.objects.get(id=pk)
    drives = Paginator(org.drive_set.all(), 5)
    context = {'org': org,
               'drives': drives.get_page(page)}
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
            return redirect('donos-organization-view', request.user.organization.id)
    else:
        form = OrganizationUpdateForm(instance=request.user.organization)

    context = {
        'form': form,
    }
    return render(request, 'donos/organization_settings.html', context=context)
