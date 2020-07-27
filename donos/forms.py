from django import forms
from .models import Notifications, Organization


class SearchForm(forms.Form):
    search = forms.CharField(label='search', max_length=30,
                             widget=forms.TextInput(attrs={'placeholder': 'Input City/Zip Code'}))


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notifications
        fields = ['title', 'description']
        # exclude = ["user"]

