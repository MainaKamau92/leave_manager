from django import forms


class EmployeesDetailsForm(forms.Form):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female')
    ]
    first_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "First Name",
            "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    last_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "Last Name",
            "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    email = forms.CharField(max_length=254, required=False, help_text='Required. Inform a valid email address.',
                            widget=forms.EmailInput(attrs={
                                'placeholder': 'Email',
                                'class': "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"}))
    job_title = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "Job Title",
            "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    official_start_date = forms.DateField(
        input_formats=['%Y-%m-%d'], required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md',
            'type': 'date'
        })
    )
    terminated = forms.BooleanField(required=False)
    sex = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md',
            'type': 'select'
        }),
        choices=SEX_CHOICES,
    )
