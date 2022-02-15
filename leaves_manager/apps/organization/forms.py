from django import forms

from leaves_manager.apps.organization.models import Organization, Country


class OrganizationForm(forms.Form):
    name = forms.CharField(max_length=250, widget=forms.TextInput(
        attrs={
            "class": "appearance-none block mb-5 w-full bg-white text-gray-900 font-medium border border-gray-400 rounded-lg py-3 px-3 leading-tight focus:outline-none"
        }
    ))
    country = forms.ModelChoiceField(
        queryset=Country.objects.all().order_by('id'),
        required=True,
        initial=1,
        widget=forms.Select(attrs={
            "class": "block w-full py-3 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500",
            "type": "select",
        })
    )

    class Meta:
        model = Organization
        fields = ('name', 'country')
