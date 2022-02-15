from django import template

from leaves_manager.apps.leaves.utils.leave_summations import (actual_days_requested)

register = template.Library()


@register.filter(name='days_requested')
def days_requested(value):
    """
    :param value: time_off_request object
    :return:
    """
    from_date, to_date, accruing, employee = (value.from_date, value.to_date,
                                              value.time_off_type.accruing, value.employee)
    days = actual_days_requested(from_date, to_date, employee)
    return f'{days} days'


@register.filter(name='tuple_slice')
def tuple_slice(value, idx):
    return value[int(idx)]
