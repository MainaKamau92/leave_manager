import calendar
import itertools
import math
from datetime import timedelta, date

import holidays
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError

from leaves_manager.apps.core.db_utils import get_query_set
from leaves_manager.apps.leaves.models import TimeOffRequest, CustomHoliday


def hours_between_date_times(from_date, to_date):
    diff = to_date - from_date
    return diff.total_seconds() / 3600


def get_default_holidays(country_name):
    present_date = date.today()
    double_named_country = {"United States of America": "US",
                            "United Kingdom": "UK",
                            "United Arab Emirates": "AE",
                            "Dominican Republic": "DO",
                            "Hong Kong": "HK",
                            "Saudi Arabia": "SA",
                            "South Africa": "ZA"}
    try:
        if country_name in double_named_country:
            default_holidays = holidays.CountryHoliday(double_named_country[country_name])
            default_holidays._populate(present_date.year)
            return default_holidays
        else:
            default_holidays = holidays.CountryHoliday(country_name)
            default_holidays._populate(present_date.year)
            return default_holidays
    except KeyError:
        return []


def weekends_in_request_range(from_date, to_date):
    """
    Checks for weekends in a date range
    :param from_date:
    :param to_date:
    :return weekends in days:
    """
    if from_date > to_date:
        raise ValidationError("The to date cannot be earlier than the from date",
                              params={'value': {'to_date': to_date, 'from_date': from_date}})
    weekend_dates = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1) if
                     (from_date + timedelta(days=x)).weekday() >= 5]
    weekend_days = len(weekend_dates)
    return weekend_days


def dates_between_two_dates(from_date, to_date):
    return [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1)]


def custom_holidays_in_request_range(from_date, to_date, organization):
    if from_date > to_date:
        raise ValidationError("The to date cannot be earlier than the from date",
                              params={'value': {'to_date': to_date, 'from_date': from_date}})
    holiday_dates = list(itertools.chain.from_iterable([dates_between_two_dates(
        i.from_date, i.to_date) for i in get_query_set(CustomHoliday, organization=organization)]))
    holidays_in_request_dates = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1) if
                                 (from_date + timedelta(days=x)) in holiday_dates]

    return dict(holidays=holidays_in_request_dates, custom_holidays=len(holidays_in_request_dates))


def holidays_in_request_range(from_date, to_date, employee):
    country_name = employee.organization.country.name
    try:
        default_holidays = [(_date, name) for _date, name in get_default_holidays(country_name).items()]
    except AttributeError:
        default_holidays = []
    if from_date > to_date:
        raise ValidationError("The to date cannot be earlier than the from date",
                              params={'value': {'to_date': to_date, 'from_date': from_date}})
    holiday_dates = [from_date + timedelta(days=x) for x in range((to_date - from_date).days + 1) if
                     (from_date + timedelta(days=x)) in default_holidays]
    holiday_days = len(holiday_dates)
    custom_holidays = custom_holidays_in_request_range(from_date, to_date, employee.organization)
    return holiday_days + custom_holidays["custom_holidays"]


def compute_approved_time_off_requests(employee, time_off_type):
    employee_approved_requests = year_scoped_time_off_check(employee.organization).filter(employee=employee,
                                                                                          time_off_type=time_off_type)
    total_hours = []
    weekend_hours = []
    holiday_days = []
    for time_off in employee_approved_requests:
        total_hours.append(hours_between_date_times(time_off.from_date, time_off.to_date))
        weekend_hours.append(weekends_in_request_range(time_off.from_date, time_off.to_date))
        holiday_days.append(holidays_in_request_range(time_off.from_date, time_off.to_date, employee))
    total_hours_approved_requests = math.fsum(total_hours)
    total_weekend_hours_in_approved_requests = math.fsum(weekend_hours)
    total_holiday_hours_in_approved_requests = math.fsum(holiday_days) * 24
    # Get the actual leave request hours
    actual_request_hours = total_hours_approved_requests - total_weekend_hours_in_approved_requests
    actual_request_hours -= total_holiday_hours_in_approved_requests
    return actual_request_hours


def year_scoped_time_off_check(organization):
    present_date = date.today()
    year_qs = get_query_set(TimeOffRequest, organization=organization).filter(
        from_date__gte=date(present_date.year, 1, 1),
        to_date__lte=date(present_date.year, 12, 31), status="AP")
    return year_qs


def time_off_accrued_to_date(employee, time_off_type):
    present_date = date.today()
    year_first_day = date(present_date.year, 1, 1)
    from_date = year_first_day if employee.official_start_date <= year_first_day else employee.official_start_date
    days_diff = (present_date - from_date).days
    time_off_per_day = time_off_type.annual_days / (366 if calendar.isleap(date.today().year) else 365)
    return time_off_per_day * days_diff


def time_off_days_remainder(employee, time_off_type):
    days_taken = compute_approved_time_off_requests(employee, time_off_type) / 24
    if time_off_type.accruing:
        accrued_days = time_off_accrued_to_date(employee, time_off_type)
        return accrued_days - days_taken
    else:
        time_off_days = time_off_type.annual_days
        return time_off_days - days_taken


def time_off_summaries(employee, time_off_type):
    gender_based_leave_types = ["Maternity Leave", "Paternity Leave"]
    days_taken = compute_approved_time_off_requests(employee, time_off_type) / 24
    print(employee.sex)

    if time_off_type.name in gender_based_leave_types:
        if time_off_type.name == "Maternity Leave" and employee.sex == "M":
            return 0.0, 0.0
        elif time_off_type.name == "Paternity Leave" and employee.sex == "F":
            return 0.0, 0.0
        else:
            time_off_days = time_off_type.annual_days
            return time_off_days, days_taken

    else:
        if time_off_type.accruing:
            accrued_days = time_off_accrued_to_date(employee, time_off_type)
            return accrued_days, days_taken
        else:
            time_off_days = time_off_type.annual_days
            return time_off_days, days_taken


def actual_days_requested(from_date, to_date, employee):
    total_days = relativedelta(to_date, from_date).days
    weekends = weekends_in_request_range(from_date, to_date)
    holidays_ = holidays_in_request_range(from_date, to_date, employee)
    return total_days - (weekends + holidays_)
