# Generated by Django 3.2 on 2021-06-05 11:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employees', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeOffType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('time_off_type_uuid', models.UUIDField(default=uuid.uuid4)),
                ('name', models.CharField(max_length=250)),
                ('annual_days', models.IntegerField(default=0)),
                ('accruing', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeofftype_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeofftype_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TimeOffRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('time_off_request_uuid', models.UUIDField(default=uuid.uuid4)),
                ('from_date', models.DateTimeField()),
                ('to_date', models.DateTimeField()),
                ('description', models.TextField(blank=True, null=True)),
                ('paid', models.BooleanField(default=True)),
                ('status', models.CharField(choices=[('AP', 'Approved'), ('PE', 'Pending'), ('RE', 'Rejected')], default='PE', max_length=2)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeoffrequest_created', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='employees.employee')),
                ('modified_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='timeoffrequest_modified', to=settings.AUTH_USER_MODEL)),
                ('time_off_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='leaves.timeofftype')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CustomHoliday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('custom_holiday_uuid', models.UUIDField(default=uuid.uuid4)),
                ('name', models.CharField(max_length=200, unique=True)),
                ('from_date', models.DateTimeField(unique=True)),
                ('to_date', models.DateTimeField(unique=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customholiday_created', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='customholiday_modified', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
