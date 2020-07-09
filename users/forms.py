from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from donos.models import Organization


class UserRegisterForm(UserCreationForm):
    # TODO Boolean Org Field
    email = forms.EmailField()
    org = forms.BooleanField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'org']


# TODO implement UserUpdateForm
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'address', 'city', 'state', 'zipcode']
        exclude = ["user"]