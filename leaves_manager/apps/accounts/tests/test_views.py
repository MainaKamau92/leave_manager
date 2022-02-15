import pytest
from django.core import mail
from django.forms import model_to_dict
from django.urls import reverse

from leaves_manager.apps.accounts.tests.factories import UserFactory
from leaves_manager.apps.accounts.utils.token_engine import generate_invitation_jwt_token, generate_password_reset_token
from leaves_manager.apps.organization.tests.factories import OrganizationFactory


@pytest.mark.django_db
def test_user_sign_up(client):
    url = reverse('sign-up')
    data = {
        'email': 'doe@glice.com',
        'password1': 'Password12@',
        'password2': 'Password12@',
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_sign_in(client):
    user = UserFactory(password='Pass123#')
    url = reverse('sign-in')
    data = {
        'email': user.email,
        'password': 'Pass123#'
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_update_personal_details(authenticated_client):
    url = reverse('settings')
    data = {
        'first_name': 'Robert',
        'last_name': 'Oppenheimer',
        'email': 'robert@manhattanproject.com',
        'job_title': 'Director',
        'personal_details': ['Update Information']
    }
    response = authenticated_client.post(url, data=data, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_update_password_from_settings(authenticated_client):
    url = reverse('settings')
    data = {
        'old_password': 'John1234$',
        'new_password': 'Atomic123@',
        'repeat_password': 'Atomic123@',
        'password_change': ['Update Password']
    }
    response = authenticated_client.post(url, data=data, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_invite_new_user(authenticated_client):
    url = reverse('settings')
    data = {
        'email': 'lewiikamaa8@gmail.com',
        'invite_user': ['Send Invitation']
    }
    response = authenticated_client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_user_can_fetch_dashboard(authenticated_client):
    url = reverse('dashboard')
    response = authenticated_client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_sign_out(authenticated_client):
    url = reverse('sign-out')
    response = authenticated_client.get(url, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_new_user_can_add_details(client):
    organization = model_to_dict(OrganizationFactory())
    token = generate_invitation_jwt_token(organization)
    url = reverse('new-user', kwargs={'invitation_token': token})
    data = {
        'first_name': 'Robert',
        'last_name': 'Oppenheimer',
        'email': 'robert@manhattanproject.com',
        'job_title': 'Director',
        'password1': 'Pass123@',
        'password2': 'Pass123@'
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200


@pytest.mark.django_db
def test_can_request_password_reset(client):
    url = reverse('password-reset-request')
    data = {
        'email': 'johndoe@glice.com'
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_can_reset_password(client, user):
    token = generate_password_reset_token(user.email)
    url = reverse('password-reset', kwargs={'reset_token': token})
    data = {
        'password1': 'Pass123@y',
        'password2': 'Pass123@y'
    }
    response = client.post(url, data=data, follow=True)
    assert response.status_code == 200
    response = client.login(email=user.email, password='Pass123@y')
    assert response
