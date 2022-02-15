from django import forms

from leaves_manager.apps.core.db_utils import get_query_set
from leaves_manager.apps.employees.models import Employee
from leaves_manager.apps.leaves.models import TimeOffRequest, TimeOffType
from leaves_manager.apps.leaves.utils.leave_summations import time_off_days_remainder, actual_days_requested


class TimeOffTypeForm(forms.Form):
    name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "Legal leave, Maternity Leave, Paternity ..",
            "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    annual_days = forms.IntegerField(required=True, min_value=1, max_value=366,
                                     widget=forms.NumberInput(
                                         attrs={
                                             "placeholder": "Days in a year",
                                             "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
                                         }
                                     ))
    accruing = forms.BooleanField(required=False,
                                  widget=forms.CheckboxInput(
                                      attrs={
                                          "class": "form-checkbox h-5 w-5 text-blue-600"
                                      }))

    def clean(self):
        annual_days = self.cleaned_data.get('annual_days')
        if annual_days > 366 or annual_days < 1:
            raise forms.ValidationError('The annual days should fall between 1 and 366')
        return self.cleaned_data


class TimeOffRequestForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('AP', 'Approved'),
        ('PE', 'Pending'),
        ('RE', 'Rejected'),
    ]

    PAYMENT_CHOICES = [
        ('FP', 'Full Pay'),
        ('HP', 'Half Pay'),
        ('NP', 'No Pay'),
    ]

    def __init__(self, user, *args, **kwargs):
        super(TimeOffRequestForm, self).__init__(*args, **kwargs)
        self.fields['employee'] = forms.ModelChoiceField(
            queryset=get_query_set(Employee, user.organization), required=True,
            widget=forms.Select(attrs={
                "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md",
                "type": "select",
            }))
        self.fields['time_off_type'] = forms.ModelChoiceField(
            queryset=get_query_set(TimeOffType, user.organization), required=True,
            widget=forms.Select(attrs={
                "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
            }))

    def clean(self):
        from_date = self.cleaned_data.get('from_date')
        to_date = self.cleaned_data.get('to_date')
        time_off_type = self.cleaned_data.get('time_off_type')
        employee = self.cleaned_data.get('employee')
        if from_date > to_date:
            raise forms.ValidationError('The from date should not be greater than the to date')
        if from_date == to_date:
            raise forms.ValidationError("The from date and to date shouldn't be the same")
        days_requested = actual_days_requested(from_date, to_date, employee)
        if days_requested <= 0:
            raise forms.ValidationError("You cannot request 0 or less days. Check that days selected don't fall on "
                                        "weekends or holidays.")
        remaining_time_off_days = int(time_off_days_remainder(employee, time_off_type))
        if remaining_time_off_days < days_requested:
            raise forms.ValidationError(f"This employee only has {remaining_time_off_days} day(s) remaining "
                                        f"for this leave type yet {days_requested} day(s) are being requested.")

    class Meta:
        model = TimeOffRequest
        fields = ('from_date', 'to_date', 'time_off_type',
                  'description', 'payment_status', 'status', 'employee')

        widgets = {
            'from_date': forms.DateInput(
                attrs={
                    'class': 'w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md',
                    'type': 'date'
                }),
            'to_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md',
                'type': 'date'
            }),
            'description': forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md",
                    'rows': 5
                }
            ),
            'status': forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
                }
            ),
            'payment_status': forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
                }
            )

        }


class CustomHolidayForm(forms.Form):
    name = forms.CharField(max_length=250, required=False, widget=forms.TextInput(
        attrs={
            "placeholder": "Holiday Name",
            "class": "w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md"
        }
    ))
    from_date = forms.DateField(required=True, widget=forms.DateInput(
        attrs={
            'class': 'w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md',
            'type': 'date'
        }))
    to_date = forms.DateField(required=True, widget=forms.DateInput(
        attrs={
            'class': 'w-full px-3 py-2 placeholder-gray-300 border border-gray-300 rounded-md',
            'type': 'date'
        }))
