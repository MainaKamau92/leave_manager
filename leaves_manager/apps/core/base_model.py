from django.db import models

from leaves_manager.apps.accounts.models import User
from leaves_manager.apps.organization.models import Organization


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, null=True, editable=False,
                                   related_name='%(class)s_created',
                                   on_delete=models.SET_NULL)
    modified_by = models.ForeignKey(User, null=True, editable=False,
                                    related_name='%(class)s_modified',
                                    on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, null=True, blank=False, on_delete=models.CASCADE)

    class Meta:
        abstract = True
