import uuid

from leaves_manager.apps.accounts.models import User
from leaves_manager.apps.core.base_model import BaseModel, models


class Employee(BaseModel):
    MALE = 'M'
    FEMALE = 'F'
    SEX = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]
    employee_uuid = models.UUIDField(default=uuid.uuid4, null=False, blank=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=False)
    first_name = models.CharField(max_length=250, null=False, blank=False)
    last_name = models.CharField(max_length=250, null=False, blank=False)
    job_title = models.CharField(max_length=250, null=True, blank=True)
    email = models.EmailField(max_length=250, null=True, blank=False)
    sex = models.CharField(max_length=2, choices=SEX)
    official_start_date = models.DateField(null=False, blank=False)
    terminated = models.BooleanField(null=False, blank=False, default=False)

    def __str__(self):
        return self.first_name
