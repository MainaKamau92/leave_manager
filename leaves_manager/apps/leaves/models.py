import uuid

from django.core.validators import MinValueValidator, MaxValueValidator

from leaves_manager.apps.core.base_model import BaseModel, models
from leaves_manager.apps.employees.models import Employee


class TimeOffType(BaseModel):
    time_off_type_uuid = models.UUIDField(default=uuid.uuid4, null=False, blank=False)
    name = models.CharField(max_length=250, null=False, blank=False)
    annual_days = models.IntegerField(null=False, blank=False, default=0,
                                      validators=[MinValueValidator(0), MaxValueValidator(366)])
    accruing = models.BooleanField(null=False, blank=False, default=False)

    class Meta:
        unique_together = ('name', 'organization',)

    def __str__(self):
        return self.name


class TimeOffRequest(BaseModel):
    APPROVED = 'AP'
    PENDING = 'PE'
    REJECTED = 'RE'

    FULL_PAY = 'FP'
    HALF_PAY = 'HP'
    NO_PAY = 'NP'

    STATUS_CHOICES = [
        (APPROVED, 'Approved'),
        (PENDING, 'Pending'),
        (REJECTED, 'Rejected'),
    ]
    PAYMENT_CHOICES = [
        (FULL_PAY, 'Full Pay'),
        (HALF_PAY, 'Half Pay'),
        (NO_PAY, 'No Pay'),
    ]
    time_off_request_uuid = models.UUIDField(default=uuid.uuid4, null=False, blank=False)
    from_date = models.DateField(null=False, blank=False)
    to_date = models.DateField(null=False, blank=False)
    time_off_type = models.ForeignKey(TimeOffType, null=True, blank=False, on_delete=models.SET_NULL)
    description = models.TextField(null=True, blank=True)
    payment_status = models.CharField(
        max_length=2,
        choices=PAYMENT_CHOICES,
        default=FULL_PAY,
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=False, blank=False)

    class Meta:
        unique_together = ('from_date', 'to_date', 'time_off_type', 'employee',)

class CustomHoliday(BaseModel):
    custom_holiday_uuid = models.UUIDField(default=uuid.uuid4, null=False, blank=False)
    name = models.CharField(max_length=200, unique=True, null=False, blank=False)
    from_date = models.DateField(unique=True, null=False, blank=False)
    to_date = models.DateField(unique=True, null=False, blank=False)

    class Meta:
        unique_together = ('name', 'organization',)
