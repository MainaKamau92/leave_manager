import factory
from django.db.models.signals import post_save
from faker import Factory, Faker

from leaves_manager.apps.accounts.models import User
from leaves_manager.apps.organization.tests.factories import OrganizationFactory

faker = Factory.create()
fake = Faker()


@factory.django.mute_signals(post_save)
class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = fake.first_name()
    last_name = fake.last_name()
    birthday_date = fake.date_between(start_date='-30y', end_date='-20y')
    email = factory.Sequence(lambda em: "user%d@glice.com" % em)
    job_title = fake.job()
    password = factory.PostGenerationMethodCall(
        'set_password',
        faker.password(length=10,
                       special_chars=True,
                       digits=True,
                       upper_case=True,
                       lower_case=True))
    organization = factory.SubFactory(OrganizationFactory)
