from django import forms


class SearchForm(forms.Form):
    search = forms.CharField(label='search', max_length=30,
                             widget=forms.TextInput(attrs={'placeholder': 'Input City/Zip Code'}))