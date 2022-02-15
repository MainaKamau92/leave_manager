import os

from django.core.mail import send_mail
from django.forms import model_to_dict
from django.template.loader import render_to_string

from leaves_manager.apps.accounts.utils.token_engine import generate_invitation_jwt_token


def send_invitation_email(email, user):
    organization = user.organization
    token = generate_invitation_jwt_token(model_to_dict(organization))
    domain = os.getenv('DOMAIN')
    context = {
        'user': user,
        'domain': domain,
        'token': token,
        'subject': 'Invitation to collaborate on Glice',
        'organization': organization
    }
    email_template = 'emails/invitation.html'

    res = send_mail(
        recipient_list=[email],
        subject=context.get('subject'),
        html_message=render_to_string(email_template, context),
        message='',
        fail_silently=False,
        from_email=None,
    )
    return res
