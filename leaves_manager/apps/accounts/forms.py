from django import forms
from django.contrib.auth.forms import UserCreationForm

from leaves_manager.apps.accounts.models import User
from leaves_manager.apps.accounts.utils.password_validator import password_validation, form_password_validation


class SignUpForm(UserCreationForm):
    email = forms.CharField(max_length=254, help_text='Required. Inform a valid email address.',
                            widget=forms.EmailInput(attrs={
                                'class': 'text-sm appearance-none border border-gray-900 rounded w-full py-2 px-3 text-gray-900 border-2 leading-tight focus:outline-none focus:shadow-outline h-10'}))
    password1 = forms.CharField(max_length=254, label='Password',
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'text-sm border border-gray-900 appearance-none rounded w-full py-2 px-3 text-gray-700 mb-1 leading-tight focus:outline-none focus:shadow-outline h-10'}))
    password2 = forms.CharField(max_length=254, label='Confirm Password',
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'text-sm border border-gray-900 appearance-none rounded w-full py-2 px-3 text-gray-700 mb-1 leading-tight focus:outline-none focus:shadow-outline h-10'}))

    error_messages = {'password_mismatch': 'Ensure that both passwords match!'}

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        form_password_validation(forms, password1, password2)
        return self.cleaned_data

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2',)


class LoginForm(forms.Form):
    email = forms.CharField(max_length=254, help_text='Required. Inform a valid email address.',
                            widget=forms.EmailInput(attrs={
                                'class': 'text-sm appearance-none rounded w-full py-2 px-3 text-gray-700 border border-gray-900 leading-tight focus:outline-none focus:shadow-outline h-10 focus:shadow-outline',
                                'id': 'email_input'}))
    password = forms.CharField(max_length=254, label='Password',
                               widget=forms.PasswordInput(attrs={'type': 'password',
                                                                 'class': 'text-sm border border-gray-900 appearance-none rounded w-full py-2 px-3 text-gray-700 mb-1 leading-tight focus:outline-none focus:shadow-outline h-10'}))
    remember_me = forms.BooleanField(required=False,
                                     widget=forms.CheckboxInput(
                                         attrs={
                                             "class": "form-checkbox mr-2 leading-tight text-blue-600"
                                         }))


class ChangePasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    old_password = forms.CharField(max_length=254, label='Password',
                                   widget=forms.PasswordInput(attrs={
                                       'placeholder': 'Password',
                                       'type': 'password',
                                       'class': "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 "
                                                "rounded-md"}))
    new_password = forms.CharField(max_length=254, label='Password',
                                   widget=forms.PasswordInput(attrs={
                                       'placeholder': 'Password',
                                       'type': 'password',
                                       'class': "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 "
                                                "rounded-md"}))
    repeat_password = forms.CharField(max_length=254, label='Password',
                                      widget=forms.PasswordInput(attrs={
                                          'placeholder': 'Password',
                                          'type': 'password',
                                          'class': "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 "
                                                   "rounded-md"}))

    def clean(self):
        error_messages = []
        user = self.request.user
        old_password, new_password, repeat_password = self.cleaned_data.values()
        if user.check_password(old_password):
            if new_password == repeat_password:
                passwd = password_validation(new_password)
                if isinstance(passwd, list) and len(passwd) > 0:
                    error_messages.extend(passwd)
            else:
                error_messages.append('New and Repeat passwords do not match.')
        else:
            error_messages.append('An invalid current password has been provided.')
        if len(error_messages) > 0:
            raise forms.ValidationError(' & '.join(error_messages))
        return self.cleaned_data


class PersonalDetailsForm(forms.Form):
    first_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "First Name",
            "class": "w-full px-3 py-3 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    last_name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "Last Name",
            "class": "w-full px-3 py-3 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    email = forms.CharField(max_length=254, required=False, help_text='Required. Inform a valid email address.',
                            widget=forms.EmailInput(attrs={
                                'placeholder': 'Email',
                                'class': "w-full px-3 py-3 placeholder-gray-300 border border-gray-300 rounded-md"}))
    job_title = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "Job Title",
            "class": "w-full px-3 py-3 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    birthday_date = forms.DateField(
        input_formats=['%Y-%m-%d'], required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-3 py-3 placeholder-gray-300 border border-gray-300 rounded-md',
            'type': 'date'
        })
    )


class InviteUserForm(forms.Form):
    email = forms.CharField(max_length=254, help_text='Required. Inform a valid email address.',
                            widget=forms.EmailInput(attrs={
                                'placeholder': 'Add Email',
                                'class': "w-full px-3 py-3 placeholder-gray-300 border border-gray-300 rounded-md"}))


class NewUserForm(PersonalDetailsForm):

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        form_password_validation(forms, password1, password2)
        return self.cleaned_data

    def save(self):
        first_name, last_name, email, job_title, birthday_date, password1, password2 = self.cleaned_data.values()
        user = User.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            job_title=job_title,
            birthday_date=birthday_date
        )
        user.set_password(password2)
        user.save()
        return user

    password1 = forms.CharField(max_length=254, label='Password',
                                widget=forms.PasswordInput(attrs={
                                    'placeholder': 'Enter Password',
                                    'type': 'password',
                                    'class': "shadow appearance-none border rounded w-full py-3 px-3 text-gray-700 "
                                             "leading-tight focus:outline-none focus:shadow-outline"}))
    password2 = forms.CharField(max_length=254, label='Confirm Password',
                                widget=forms.PasswordInput(attrs={
                                    'placeholder': 'Confirm Password',
                                    'type': 'password',
                                    'class': "shadow appearance-none border rounded w-full py-3 px-3 text-gray-700 "
                                             "leading-tight focus:outline-none focus:shadow-outline"}))


class PasswordResetRequestForm(forms.Form):
    email = forms.CharField(max_length=254, help_text='Required. Inform a valid email address.',
                            widget=forms.EmailInput(attrs={
                                'class': 'text-sm appearance-none rounded w-full py-3 px-3 text-gray-700 border border-gray-900 leading-tight focus:outline-none focus:shadow-outline h-10'}))


class PasswordResetForm(forms.Form):
    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        form_password_validation(forms, password1, password2)
        return self.cleaned_data

    email = forms.CharField(max_length=254, disabled=True, required=False,
                            help_text='Required. Inform a valid email address.',
                            widget=forms.EmailInput(attrs={
                                'class': 'text-sm appearance-none rounded w-full py-3 px-3 text-gray-700 border border-gray-900 leading-tight focus:outline-none focus:shadow-outline h-10'}))
    password1 = forms.CharField(max_length=254, label='Password',
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'text-sm border-2 appearance-none border border-gray-900 rounded w-full py-3 px-3 text-gray-700 mb-1 leading-tight focus:outline-none focus:shadow-outline h-10'}))
    password2 = forms.CharField(max_length=254, label='Confirm Password',
                                widget=forms.PasswordInput(attrs={
                                    'type': 'password',
                                    'class': 'text-sm border-2 appearance-none rounded border border-gray-900 w-full py-3 px-3 text-gray-700 mb-1 leading-tight focus:outline-none focus:shadow-outline h-10'}))
