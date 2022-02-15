from django.shortcuts import render

from leaves_manager.apps.core.db_utils import get_query_set
from leaves_manager.apps.employees.models import Employee
from leaves_manager.apps.leaves.models import TimeOffType
from leaves_manager.apps.leaves.utils.leave_summations import time_off_summaries


def time_off_request_list(request):
    final_data = []
    time_off_types = get_query_set(TimeOffType, organization=request.user.organization)
    employees = get_query_set(Employee, organization=request.user.organization)
    [print(i.organization, i.sex) for i in employees]
    for employee in employees:
        emp_data = [time_off_summaries(employee, time_off_type) for time_off_type in time_off_types]
        # import pdb;
        # pdb.set_trace()

        final_data.append((employee, emp_data))
    return render(request, 'reports/reports.html', {'final_data': final_data,
                                                    'type_names': [i.name for i in time_off_types]})
