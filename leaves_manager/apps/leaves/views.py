from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from leaves_manager.apps.core.db_utils import get_query_set, get_model_object
from leaves_manager.apps.employees.models import Employee
from leaves_manager.apps.leaves.forms import TimeOffRequestForm, TimeOffTypeForm, CustomHolidayForm
from leaves_manager.apps.leaves.models import TimeOffRequest, TimeOffType, CustomHoliday
from leaves_manager.apps.leaves.utils.leave_summations import get_default_holidays


class TimeOffRequestsView(LoginRequiredMixin, View):
    template_name = 'leaves/time_off_requests.html'

    def get(self, request, *args, **kwargs):
        time_off_requests = get_query_set(TimeOffRequest, organization=request.user.organization)
        return render(request, self.template_name, {'time_off_requests': time_off_requests})


class NewTimeOffRequestsView(LoginRequiredMixin, View):
    template_name = 'leaves/new_time_off_request.html'

    def get(self, request, *args, **kwargs):
        time_off_requests = get_query_set(TimeOffRequest, organization=request.user.organization)
        employee_qs = get_query_set(Employee, organization=request.user.organization)
        time_off_type_qs = get_query_set(TimeOffType, organization=request.user.organization)
        employee_default = employee_qs[0].pk if len(employee_qs) > 0 else None
        time_off_type_default = time_off_type_qs[0].pk if len(time_off_type_qs) > 0 else None
        return render(request, self.template_name,
                      {'time_off_request_form': TimeOffRequestForm(data=request.POST or None, user=request.user or None,
                                                                   initial={
                                                                       'from_date': date.today(),
                                                                       'to_date': date.today(),
                                                                       'employee': employee_default,
                                                                       'time_off_type': time_off_type_default,
                                                                       'payment_status': 'FP',
                                                                   }),
                       'time_off_requests': time_off_requests})

    def post(self, request, *args, **kwargs):
        time_off_request_form = TimeOffRequestForm(data=request.POST or None, user=request.user)
        if time_off_request_form.is_valid():
            time_off_request_form.cleaned_data['organization'] = request.user.organization
            time_off = TimeOffRequest.objects.create(**time_off_request_form.cleaned_data)
            time_off.save()
            messages.add_message(request, messages.SUCCESS, "Your time off request has been created successfully!")
            return HttpResponseRedirect('/time-off/requests')
        else:
            for error in time_off_request_form.errors:
                messages.add_message(request, messages.ERROR, time_off_request_form.errors.get(error))
            time_off_requests = get_query_set(TimeOffRequest, organization=request.user.organization)
            employee_qs = get_query_set(Employee, organization=request.user.organization)
            time_off_type_qs = get_query_set(TimeOffType, organization=request.user.organization)
            employee_default = employee_qs[0].pk if len(employee_qs) > 0 else None
            time_off_type_default = time_off_type_qs[0].pk if len(time_off_type_qs) > 0 else None
            return render(request, self.template_name,
                          {'time_off_request_form': TimeOffRequestForm(data=request.POST or None,
                                                                       user=request.user or None,
                                                                       initial={
                                                                           'from_date': date.today(),
                                                                           'to_date': date.today(),
                                                                           'employee': employee_default,
                                                                           'time_off_type': time_off_type_default,
                                                                           'payment_status': 'FP',
                                                                       }),
                           'time_off_requests': time_off_requests})


class EditTimeOffRequestView(View):
    template_name = 'leaves/edit_time_off_request.html'

    def get(self, request, *args, **kwargs):
        time_off_request_uuid = kwargs.get('time_off_request_uuid')
        time_off_request = get_model_object(TimeOffRequest, 'time_off_request_uuid', time_off_request_uuid)
        return render(request, self.template_name,
                      {'time_off_request_edit_form': TimeOffRequestForm(data=request.POST or None,
                                                                        user=request.user or None,
                                                                        initial={
                                                                            'from_date': time_off_request.from_date,
                                                                            'to_date': time_off_request.to_date,
                                                                            'employee': time_off_request.employee,
                                                                            'time_off_type': time_off_request.time_off_type,
                                                                            'status': time_off_request.status,
                                                                            'description': time_off_request.description,
                                                                            'payment_status': time_off_request.payment_status,
                                                                        }
                                                                        )})

    @staticmethod
    def post(request, *args, **kwargs):
        time_off_request_uuid = kwargs.get('time_off_request_uuid')
        time_off_request = get_model_object(TimeOffRequest, 'time_off_request_uuid', time_off_request_uuid)
        edit_form = TimeOffRequestForm(data=request.POST or None, user=request.user or None, )
        if 'delete_time_off_request' in request.POST:
            time_off_request.delete()
            messages.add_message(request, messages.SUCCESS, 'Time off deleted successfully!')
            return HttpResponseRedirect('/time-off/requests/')
        if edit_form.is_valid():
            TimeOffRequest.objects.filter(time_off_request_uuid=time_off_request.time_off_request_uuid).update(
                **edit_form.cleaned_data)
            return HttpResponseRedirect('/time-off/requests/')
        else:
            for error in edit_form.errors:
                messages.add_message(request, messages.ERROR, edit_form.errors.get(error))
            return HttpResponseRedirect('/time-off/requests/')


class NewTimeOffTypeView(LoginRequiredMixin, View):
    template_name = 'leaves/new_time_off_type.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'time_off_type_form': TimeOffTypeForm()})

    @staticmethod
    def post(request, *args, **kwargs):
        time_off_type_form = TimeOffTypeForm(data=request.POST)
        if time_off_type_form.is_valid():
            time_off_type_form.cleaned_data['organization'] = request.user.organization
            time_off_type = TimeOffType.objects.create(**time_off_type_form.cleaned_data)
            time_off_type.save()
            messages.add_message(request, messages.SUCCESS, "Your time off type has been created successfully!")
            return HttpResponseRedirect('/dashboard')
        else:
            for error in time_off_type_form.errors:
                messages.add_message(request, messages.ERROR, time_off_type_form.errors.get(error))
            return HttpResponseRedirect('/type/new')


class TimeOffTypesView(LoginRequiredMixin, View):
    template_name = 'leaves/time_off_types.html'

    def get(self, request, *args, **kwargs):
        time_off_types = get_query_set(TimeOffType, organization=request.user.organization)
        return render(request, self.template_name, {'time_off_types': time_off_types})


class EditTimeOffTypeView(View):
    template_name = 'leaves/edit_time_off_type.html'

    def get(self, request, *args, **kwargs):
        time_off_type_uuid = kwargs.get('time_off_type_uuid')
        time_off_type = get_model_object(TimeOffType, 'time_off_type_uuid', time_off_type_uuid)
        return render(request, self.template_name,
                      {'time_off_type_edit_form': TimeOffTypeForm(initial={
                          'name': time_off_type.name,
                          'annual_days': time_off_type.annual_days,
                          'accruing': time_off_type.accruing
                      })})

    @staticmethod
    def post(request, *args, **kwargs):
        time_off_type_uuid = kwargs.get('time_off_type_uuid')
        time_off_type = get_model_object(TimeOffType, 'time_off_type_uuid', time_off_type_uuid)
        edit_form = TimeOffTypeForm(request.POST)
        if 'delete_time_off_type' in request.POST:
            time_off_type.delete()
            messages.add_message(request, messages.SUCCESS, 'Time off type deleted successfully!')
            return HttpResponseRedirect('/dashboard/')
        if edit_form.is_valid():
            TimeOffType.objects.filter(time_off_type_uuid=time_off_type.time_off_type_uuid).update(
                **edit_form.cleaned_data)
            messages.add_message(request, messages.SUCCESS, 'Time off type updated successfully!')
            return HttpResponseRedirect('/dashboard/')
        else:
            for error in edit_form.errors:
                messages.add_message(request, messages.ERROR, edit_form.errors.get(error))
            return HttpResponseRedirect(f'/time-off/type/edit/{time_off_type_uuid}')


class NewCustomHolidayView(View):
    template_name = 'leaves/new_custom_holiday.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'custom_holiday_form': CustomHolidayForm()})

    def post(self, request, *args, **kwargs):
        holiday_form = CustomHolidayForm(request.POST)
        if holiday_form.is_valid():
            holiday_form.cleaned_data['organization'] = request.user.organization
            custom_holiday = CustomHoliday.objects.create(**holiday_form.cleaned_data)
            custom_holiday.save()
            messages.add_message(request, messages.SUCCESS, "Your custom holiday has been created successfully!")
            return HttpResponseRedirect('/dashboard/')


class EditCustomHolidayView(View):
    template_name = 'leaves/edit_custom_holiday.html'

    def get(self, request, *args, **kwargs):
        custom_holiday_uuid = kwargs.get('custom_holiday_uuid')
        custom_holiday = get_model_object(CustomHoliday, 'custom_holiday_uuid', custom_holiday_uuid)
        return render(request, self.template_name,
                      {'custom_holiday_edit_form': CustomHolidayForm(initial={
                          'name': custom_holiday.name,
                          'from_date': custom_holiday.from_date,
                          'to_date': custom_holiday.to_date
                      })})

    @staticmethod
    def post(request, *args, **kwargs):
        custom_holiday_uuid = kwargs.get('custom_holiday_uuid')
        custom_holiday = get_model_object(CustomHoliday, 'custom_holiday_uuid', custom_holiday_uuid)
        edit_form = CustomHolidayForm(request.POST)
        if 'delete_custom_holiday' in request.POST:
            custom_holiday.delete()
            messages.add_message(request, messages.SUCCESS, 'Custom Holiday deleted successfully!')
            return HttpResponseRedirect('/dashboard/')
        if edit_form.is_valid():
            CustomHoliday.objects.filter(custom_holiday_uuid=custom_holiday.custom_holiday_uuid).update(
                **edit_form.cleaned_data)
            messages.add_message(request, messages.SUCCESS, 'Custom Holiday updated successfully!')
            return HttpResponseRedirect('/dashboard/')
        else:
            for error in edit_form.errors:
                messages.add_message(request, messages.ERROR, edit_form.errors.get(error))
            return HttpResponseRedirect(f'custom-holidays/edit/{custom_holiday_uuid}')


class HolidaysView(View):
    template_name = 'leaves/custom_holidays.html'

    def get(self, request, *args, **kwargs):
        country_name = request.user.organization.country.name
        custom_holidays = get_query_set(CustomHoliday, organization=request.user.organization)

        try:
            default_holidays = [(_date, name) for _date, name in get_default_holidays(country_name).items()]
            print(default_holidays)
            return render(request, self.template_name, {'custom_holidays': custom_holidays,
                                                        'default_holidays': default_holidays,
                                                        'holidays_exist': True if len(list(custom_holidays) + default_holidays) > 0 else False})
        except AttributeError:
            default_holidays = []
            return render(request, self.template_name, {'custom_holidays': custom_holidays,
                                                        'default_holidays': default_holidays,
                                                        'holidays_exist': True if len(list(custom_holidays) + default_holidays) > 0 else False})
