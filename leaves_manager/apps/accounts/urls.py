from django.urls import path

from leaves_manager.apps.accounts.views import (SettingsView, DashboardView, SignInView, SignUpView,
                                                SignOutView, NewUserView, PasswordResetRequestView, PasswordResetView,
                                                SlackIntegrationView, VerifyEmailView)

urlpatterns = [
    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('sign-in/', SignInView.as_view(), name='sign-in'),
    path('sign-out/', SignOutView.as_view(), name='sign-out'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    path('settings/', SettingsView.as_view(), name='settings'),
    path('verify-email/<str:user_token>', VerifyEmailView.as_view(), name='verify-email'),
    path('new-user/<str:invitation_token>', NewUserView.as_view(), name='new-user'),
    path('password-reset-request', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('password-reset/<str:reset_token>', PasswordResetView.as_view(), name='password-reset'),
    path('slack-integration', SlackIntegrationView.as_view(), name='slack-integration')
]
