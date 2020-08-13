from crispy_forms.bootstrap import StrictButton
from django import forms
from django.forms import formset_factory
from .models import Notifications, Organization, Drive, Category, DonationItem
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit, MultiField, Div


class SearchForm(forms.Form):
    search = forms.CharField(label='search', max_length=30,
                             widget=forms.TextInput(attrs={'placeholder': 'Input City/Zip Code'}))


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notifications
        fields = ['title', 'description']
        # exclude = ["user"]


class DriveForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects, widget=forms.CheckboxSelectMultiple(),
                                            required=True)
    class Meta:
        model = Drive
        fields = ['title', 'content', 'start_date', 'end_date', 'address', 'city', 'state', 'zipcode', 'categories']


class DonationForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.none(),widget=forms.Select(), required=True)

    class Meta:
        model = DonationItem
        fields = ['name', 'quantity', 'category','donation']
        exclude = ['donation']

    def __init__(self, id, *args, **kwargs):
        super(DonationForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Item Name"
        self.fields['quantity'].label = "Item Quantity"
        self.fields['category'] = forms.ModelChoiceField(queryset=Drive.objects.filter(id=id).first().category.all())
        self.helper = FormHelper()
        self.helper.form_method = 'POST'

class DonationFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(
            Div(
                'name',
                css_class='form-group',
            ),
            Div(
                Div(
                    'quantity',
                    css_class='form-group col-md-6',
                ),
                Div(
                    'category',
                    css_class='form-group col-md-6',
                ),
                css_class='form-row',
            )
        )
        self.render_required_fields = True
        self.add_input(Submit("submit", "Save"))
        self.add_input(Submit("form_add", "Add"))
        self.add_input(Submit("form_remove", "Remove"))