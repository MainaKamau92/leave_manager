import factory
from faker import Factory, Faker

from leaves_manager.apps.organization.models import Organization

faker = Factory.create()
fake = Faker()


class OrganizationFactory(factory.DjangoModelFactory):
    class Meta:
        model = Organization

    name = fake.company()
    slack_workspace_id = 'CH' + fake.word().upper() + '0X1'
    country = faker.country()
    initial_set_up_complete = fake.boolean()
