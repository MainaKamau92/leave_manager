import uuid

from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class Organization(models.Model):
    org_uuid = models.UUIDField(default=uuid.uuid4, null=False, blank=False, unique=True)
    name = models.CharField(max_length=250, null=True, blank=False)
    country = models.ForeignKey(Country, null=True, blank=False, on_delete=models.SET_NULL)
    initial_set_up_complete = models.BooleanField(null=False, blank=False, default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    slack_integrated = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class SlackIntegration(models.Model):
    slack_team_id = models.CharField(max_length=250, null=True, blank=False)
    slack_team_name = models.CharField(max_length=250, null=True, blank=False)
    organization = models.ForeignKey(Organization, null=True, blank=False, on_delete=models.CASCADE)
    bot_user_id = models.CharField(max_length=250, null=True, blank=False)
    app_id = models.CharField(max_length=250, null=True, blank=False)
    access_token = models.CharField(max_length=1000, null=True, blank=False)
    channel = models.CharField(max_length=250, null=True, blank=False)
    channel_id = models.CharField(max_length=250, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
