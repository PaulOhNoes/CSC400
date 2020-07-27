from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from donos.models import Organization


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# TODO implement UserUpdateForm
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'address', 'city', 'state', 'zipcode']
        # exclude = ('user',)


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'address', 'city', 'state', 'zipcode', 'file']
        exclude = ["user"]


class OrganizationUpdateForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'description', 'address', 'city', 'state', 'zipcode', 'file']