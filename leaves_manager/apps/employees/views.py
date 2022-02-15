from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from leaves_manager.apps.core.db_utils import get_model_object, get_query_set
from leaves_manager.apps.employees.forms import EmployeesDetailsForm
from leaves_manager.apps.employees.models import Employee


class EmployeesView(View):
    template_name = 'employees/employees.html'

    def get(self, request, *args, **kwargs):
        employees = get_query_set(Employee, request.user.organization)
        return render(request, self.template_name, {'employees': employees})


class NewEmployeesView(View):
    template_name = 'employees/new_employee.html'
    form = EmployeesDetailsForm()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'new_employee_form': self.form})

    @staticmethod
    def post(request, *args, **kwargs):
        organization = request.user.organization
        new_employee_form = EmployeesDetailsForm(request.POST)
        if new_employee_form.is_valid():
            new_employee_form.cleaned_data['organization'] = organization
            employee = Employee.objects.create(**new_employee_form.cleaned_data)
            employee.save()
            messages.add_message(request, messages.SUCCESS, 'Employee created successfully!')
            return HttpResponseRedirect('/employees')
        else:
            for error in new_employee_form.errors:
                messages.add_message(request, messages.ERROR, new_employee_form.errors.get(error))
            return HttpResponseRedirect('/employees/new')


class EditEmployeesView(View):
    template_name = 'employees/edit_employee.html'
    form = EmployeesDetailsForm()

    def get(self, request, *args, **kwargs):
        employee_id = kwargs.get('employee_uuid')
        employee = get_model_object(Employee, 'employee_uuid', employee_id)
        return render(request, self.template_name, {'edit_form': EmployeesDetailsForm(
            initial={
                'first_name': employee.first_name,
                'last_name': employee.last_name,
                'email': employee.email,
                'job_title': employee.job_title,
                'official_start_date': employee.official_start_date,
                'terminated': employee.terminated,
                'sex': employee.sex,
            }
        )})

    @staticmethod
    def post(request, *args, **kwargs):
        employee_uuid = kwargs.get('employee_uuid')
        employee = get_model_object(Employee, 'employee_uuid', employee_uuid)
        if 'delete_employee' in request.POST:
            employee.delete()
            messages.add_message(request, messages.SUCCESS, 'Employee deleted successfully!')
            return redirect('employees')
        edit_form = EmployeesDetailsForm(request.POST)
        if edit_form.is_valid():
            Employee.objects.filter(employee_uuid=employee.employee_uuid).update(**edit_form.cleaned_data)
            return redirect('employees')
        else:
            for error in edit_form.errors:
                messages.add_message(request, messages.ERROR, edit_form.errors.get(error))
            return HttpResponseRedirect(f'/employees/edit/{employee_uuid}')
