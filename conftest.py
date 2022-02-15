import pytest

from leaves_manager.apps.accounts.tests.factories import UserFactory


@pytest.fixture
@pytest.mark.django_db
def user():
    user = UserFactory(
        first_name='John',
        last_name='Doe',
        email='john@glice.com',
        password='John1234$',
        is_verified=True,
        is_org_owner=True
    )
    return user


@pytest.fixture
@pytest.mark.django_db
def authenticated_client(client, user):
    client.force_login(user)
    client.login(username=user.email, password=user.password)
    yield client
