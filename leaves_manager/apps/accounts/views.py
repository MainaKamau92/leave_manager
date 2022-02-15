import os
from datetime import datetime, timedelta

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.views.generic import View

from leaves_manager.apps.accounts.forms import SignUpForm, LoginForm, ChangePasswordForm, PersonalDetailsForm, \
    InviteUserForm, NewUserForm, PasswordResetRequestForm, PasswordResetForm
from leaves_manager.apps.accounts.models import User
from leaves_manager.apps.accounts.utils.emails.email_verification import send_verification_link_email
from leaves_manager.apps.accounts.utils.emails.invitation import send_invitation_email
from leaves_manager.apps.accounts.utils.emails.password_reset import send_password_reset_email
from leaves_manager.apps.accounts.utils.token_engine import decode_token
from leaves_manager.apps.core.db_utils import get_model_object, get_query_set
from leaves_manager.apps.employees.models import Employee
from leaves_manager.apps.leaves.models import TimeOffRequest, TimeOffType, CustomHoliday
from leaves_manager.apps.organization.models import Organization, SlackIntegration
from leaves_manager.integrations.slack import SlackCentral


class SettingsView(LoginRequiredMixin, View):
    template_name = 'accounts/settings.html'

    def _renderer(self, request, slack_integrated, user):
        return render(request, self.template_name, self.get_context_data(request=request,
                                                                         slack_integrated=slack_integrated,
                                                                         personal_details_form=PersonalDetailsForm(
                                                                             initial={
                                                                                 'first_name': user.first_name,
                                                                                 'last_name': user.last_name,
                                                                                 'email': user.email,
                                                                                 'job_title': user.job_title,
                                                                                 'birthday_date': user.birthday_date,
                                                                             }
                                                                         )))

    @staticmethod
    def get_context_data(**kwargs):
        if 'change_password_form' not in kwargs:
            kwargs['change_password_form'] = ChangePasswordForm(request=kwargs.get('request'))
        if 'personal_details_form' not in kwargs:
            kwargs['personal_details_form'] = PersonalDetailsForm()
        if 'invite_user_form' not in kwargs:
            kwargs['invite_user_form'] = InviteUserForm()
        return kwargs

    def get(self, request, *args, **kwargs):
        user = request.user
        slack_integrated = get_query_set(SlackIntegration, organization=user.organization).exists()
        return self._renderer(request, slack_integrated, user)

    def post(self, request, *args, **kwargs):
        user = request.user
        ctxt = {}
        slack_integrated = get_query_set(SlackIntegration, organization=user.organization).exists()

        if 'personal_details' in request.POST:
            personal_details_form = PersonalDetailsForm(request.POST)
            if personal_details_form.is_valid():
                email = personal_details_form.cleaned_data.get("email")
                personal_details_form.cleaned_data.pop("email") if user.email == email else None
                User.objects.filter(user_uuid=user.user_uuid).update(**personal_details_form.cleaned_data)
                return self._renderer(request, slack_integrated, user)
            else:
                ctxt['personal_details_form'] = personal_details_form
                for error in personal_details_form.errors:
                    messages.add_message(request, messages.ERROR, personal_details_form.errors.get(error))
                return self._renderer(request, slack_integrated, user)

        elif 'password_change' in request.POST:
            change_password_form = ChangePasswordForm(data=request.POST, request=request)
            if change_password_form.is_valid():
                new_password = change_password_form.cleaned_data['new_password']
                if new_password:
                    user.set_password(new_password)
                    user.save()
                    messages.add_message(request, messages.SUCCESS, "Your password was changed successfully!")
                    return self._renderer(request, slack_integrated, user)
            else:
                ctxt['change_password_form'] = change_password_form
                for error in change_password_form.errors:
                    messages.add_message(request, messages.ERROR, change_password_form.errors.get(error))
                return self._renderer(request, slack_integrated, user)

        elif 'invite_user' in request.POST:
            invite_user_form = InviteUserForm(request.POST)
            if invite_user_form.is_valid():
                email = invite_user_form.cleaned_data.get('email')
                user = User.objects.get(email=email)
                if user:
                    messages.add_message(request, messages.ERROR, "A user with that email already exists!")
                    return self._renderer(request, slack_integrated, user)
                else:
                    response = send_invitation_email(email, user=user)
                    if response == 1:
                        messages.add_message(request, messages.SUCCESS, "Email dispatched successfully!")
                    elif response == 0:
                        messages.add_message(request, messages.ERROR, "Failed to send the email!")
                    return self._renderer(request, slack_integrated, user)
            else:
                ctxt['invite_user_form'] = invite_user_form

        return render(request, self.template_name, self.get_context_data(**ctxt))


class DashboardView(LoginRequiredMixin, View):
    template_name = 'accounts/dashboard.html'

    def get(self, request, *args, **kwargs):
        organization = request.user.organization
        present_date = datetime.now()
        mon = present_date - timedelta(days=present_date.weekday())
        mon_midnight = datetime(mon.year, mon.month, mon.day, 0, 0)
        saturday_midnight = present_date + timedelta(days=5)
        approved_time_off_requests = get_query_set(TimeOffRequest,
                                                   organization).filter(status='AP').values('employee').distinct()
        rejected_time_off_requests = get_query_set(TimeOffRequest, organization).filter(status='PE')
        time_off_types = get_query_set(TimeOffType, organization)
        holidays = get_query_set(CustomHoliday, organization)
        weeks_time_off_requests = get_query_set(TimeOffRequest, organization, distinct_qs='employee').filter(
            to_date__gte=mon_midnight,
            to_date__lte=saturday_midnight)
        employees = get_query_set(Employee, organization)
        return render(request, self.template_name, {'ooo_count': approved_time_off_requests.count(),
                                                    'pending_count': rejected_time_off_requests.count(),
                                                    'employees_count': employees.count(),
                                                    'time_off_types': time_off_types[:3],
                                                    'holidays': holidays[:3],
                                                    'week_time_off': weeks_time_off_requests[:3]})


class SignInView(View):
    template_name = 'accounts/login.html'
    form = LoginForm()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form})

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(username=email, password=password)

            if user is not None:
                if not user.is_verified:
                    messages.add_message(request, messages.ERROR, "This user's email has not been verified."
                                                                  "Check your inbox for the verification link.")
                    return render(request, 'accounts/login.html', {'form': form})
                if not form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(0)
                login(request=request, user=user)
                if user.organization is None or user.organization == '':
                    return redirect('new-organization')
                else:
                    path_to_follow = request.get_full_path().split('/')
                    if '?next=' in path_to_follow:
                        return redirect(request.GET.get('next'))
                    else:
                        return redirect('dashboard')
            else:
                messages.add_message(request, messages.ERROR, "Incorrect username or password.")
                return render(request, 'accounts/login.html', {'form': form})
        else:
            for error in form.errors:
                messages.add_message(request, messages.ERROR, form.errors.get(error))
            return render(request, 'accounts/login.html', {'form': form})


class SignUpView(View):
    template_name = 'accounts/signup.html'
    form = SignUpForm()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form})

    @staticmethod
    def post(request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            users = User.objects.filter(email=email)
            if users.count() > 0:
                messages.add_message(request, messages.ERROR, "A user with that email already exists.")
                return render(request, 'accounts/signup.html', {'form': form})
            else:
                form.save()
                response = send_verification_link_email(email)
                if response == 1:
                    messages.add_message(request, messages.SUCCESS,
                                         "A verification email has been sent to the email you provided")
                    return HttpResponseRedirect('/sign-in/')
                elif response == 0:
                    messages.add_message(request, messages.ERROR, "Something wrong happened and we could not complete "
                                                                  "the request, kindly reach out to our customer care "
                                                                  "department for assistance! Thank you for your "
                                                                  "patience.")
                    return redirect('sign-in')
                return redirect('sign-in')
        else:
            for error in form.errors:
                messages.add_message(request, messages.ERROR, form.errors.get(error))
            return render(request, 'accounts/signup.html', {'form': form})


class VerifyEmailView(View):
    template_name = 'email/verification_success.html'
    form = SignUpForm()

    def get(self, request, *args, **kwargs):
        user_token = kwargs.get('user_token')
        payload = decode_token(user_token)
        if payload is not None:
            user = get_model_object(User, 'email', payload.get('email'))
            if user is None:
                messages.add_message(request, messages.ERROR, 'That user does not exist in our system!')
                return redirect('sign-in')
            else:
                user.is_verified = True
                user.save()
                messages.add_message(request, messages.SUCCESS, 'Your email has been successfully verified')
                return redirect('sign-in')

        else:
            messages.add_message(request, messages.ERROR, 'The token you are using has expired or is no longer valid.')
            return redirect('sign-in')


class SignOutView(View):

    @staticmethod
    def get(request, *args, **kwargs):
        logout(request)
        return redirect('sign-in')


class NewUserView(View):
    template_name = 'accounts/new_user.html'
    new_user_form = NewUserForm()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'new_user_form': self.new_user_form})

    @staticmethod
    def post(request, *args, **kwargs):
        form = NewUserForm(request.POST)
        invitation_token = kwargs.get('invitation_token')
        payload = decode_token(invitation_token)
        if payload is not None:
            organization = get_model_object(Organization, 'org_uuid', payload.get('org_uuid'))
            if organization is None:
                messages.add_message(request, messages.ERROR, 'That organization does not exist in our system!')
                return HttpResponseRedirect(f'/new-user/{invitation_token}')
            else:
                if form.is_valid():
                    user = form.save()
                    user.organization = organization
                    user.save()
                    messages.add_message(request, messages.SUCCESS,
                                         'Your account has been created successfully you may log in now!')
                    return HttpResponseRedirect(f'/sign-in')
                else:
                    for error in form.errors:
                        messages.add_message(request, messages.ERROR, form.errors.get(error))
                    return HttpResponseRedirect(f'/new-user/{invitation_token}')

        else:
            for error in form.errors:
                messages.add_message(request, messages.ERROR, form.errors.get(error))
            return HttpResponseRedirect(f'/new-user/{invitation_token}')


class PasswordResetRequestView(View):
    template_name = 'accounts/password_reset_request.html'
    password_reset_request_form = PasswordResetRequestForm()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'password_reset_request_form': self.password_reset_request_form})

    def post(self, request, *args, **kwargs):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = get_model_object(User, 'email', email)
            if user:
                response = send_password_reset_email(email)
                if response == 1:
                    messages.add_message(request, messages.SUCCESS,
                                         "Your password reset instructions have been sent to your email!")
                    return HttpResponseRedirect('/sign-in')
                elif response == 0:
                    messages.add_message(request, messages.ERROR, "Something wrong happened and we could not complete "
                                                                  "the request, kindly reach out to our customer care "
                                                                  "department for assistance! Thank you for your "
                                                                  "patience.")
                return HttpResponseRedirect('/password-reset-request')
            else:
                for error in form.errors:
                    messages.add_message(request, messages.ERROR, form.errors.get(error))
                return HttpResponseRedirect(f'/password-reset-request')


class PasswordResetView(View):
    template_name = 'accounts/password_reset.html'
    password_reset_form = PasswordResetForm()

    def get(self, request, *args, **kwargs):
        reset_token = kwargs.get('reset_token')
        payload = decode_token(reset_token)
        if payload is not None:
            return render(request, self.template_name, {'password_reset_form': PasswordResetForm(initial={
                'email': payload.get('email'),
            })})
        else:
            messages.add_message(request, messages.ERROR, "The token provided has expired or is invalid!")
            return render(request, self.template_name, {'password_reset_form': self.password_reset_form})

    @staticmethod
    def post(request, *args, **kwargs):
        form = PasswordResetForm(request.POST)
        reset_token = kwargs.get('reset_token')
        payload = decode_token(reset_token)
        if payload is not None:
            user = get_model_object(User, 'email', payload.get('email'))
            if user is None:
                messages.add_message(request, messages.ERROR, 'A user with this email does not exist in our system!')
                return HttpResponseRedirect(f'/password-reset/{reset_token}')
            else:
                if form.is_valid():
                    password = form.cleaned_data.get('password2')
                    user.set_password(password)
                    user.save()
                    messages.add_message(request, messages.SUCCESS, "Your password has been reset successfully. "
                                                                    "You can login!")
                    return HttpResponseRedirect(f'/sign-in')
                else:
                    for error in form.errors:
                        messages.add_message(request, messages.ERROR, form.errors.get(error))
                    return HttpResponseRedirect(f'/password-reset/{reset_token}')

        else:
            messages.add_message(request, messages.ERROR, "The token provided has expired or is invalid!")
            return HttpResponseRedirect(f'/password-reset/{reset_token}')


class SlackIntegrationView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            temp_access_token = request.GET['code']
            payload = {
                "client_id": os.getenv("SLACK_CLIENT_ID"),
                "client_secret": os.getenv("SLACK_CLIENT_SECRET"),
                "code": temp_access_token,
                "grant_type": "authorization_code",
                "redirect_uri": os.getenv("SLACK_REDIRECT_URI"),
                "refresh_token": ""
            }
            response = requests.post("https://slack.com/api/oauth.v2.access", data=payload)
            organization = request.user.organization
            if response.ok:
                data = response.json()
                slack_team_id = data["team"]["id"]
                slack_team_name = data["team"]["name"]
                bot_user_id = data["bot_user_id"]
                app_id = data["app_id"]
                access_token = data["access_token"]
                channel_name = data["incoming_webhook"]["channel"]
                channel_id = data["incoming_webhook"]["channel_id"]
                slack_integration = SlackIntegration.objects.create(slack_team_id=slack_team_id,
                                                                    slack_team_name=slack_team_name,
                                                                    bot_user_id=bot_user_id, app_id=app_id,
                                                                    access_token=access_token,
                                                                    channel=channel_name, channel_id=channel_id,
                                                                    organization=organization)
                slack_integration.save()
                organization.slack_integrated = True
                organization.save()
                sc = SlackCentral(access_token)
                sc.join_conversation(channel=channel_id)
                blocks = {
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "Hello <!here> :wave:"
                            }
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "I am the Glice Bot and Glad to be here! \n I'll be helping with updating the "
                                        "team on who is out of office for the week. "
                            }
                        }
                    ]
                }
                sc.post_to_channel(channel=channel_id, message="Hello :wave:", blocks=blocks["blocks"])
                messages.add_message(request, messages.SUCCESS, 'Slack Integration was completed successfully!')
                return HttpResponseRedirect('/dashboard/')
            else:
                messages.add_message(request, messages.ERROR, 'Slack Integration failed!')
                return HttpResponseRedirect('/dashboard/')
        except MultiValueDictKeyError:
            messages.add_message(request, messages.ERROR, 'Slack Integration failed!')
            return HttpResponseRedirect('/dashboard/')
