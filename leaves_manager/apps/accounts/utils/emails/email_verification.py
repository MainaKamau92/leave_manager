import os

from django.core.mail import send_mail
from django.template.loader import render_to_string

from leaves_manager.apps.accounts.utils.token_engine import generate_email_verification_token


def send_verification_link_email(email):
    token = generate_email_verification_token(email)
    domain = os.getenv('DOMAIN')
    context = {
        'domain': domain,
        'token': token,
        'subject': 'Verify Your Email',
    }
    email_template = 'emails/email_verification.html'
    res = send_mail(
        recipient_list=[email],
        subject=context.get('subject'),
        html_message=render_to_string(email_template, context),
        message='',
        fail_silently=False,
        from_email=None,
    )
    return res
