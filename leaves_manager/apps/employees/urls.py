from django.urls import path

from leaves_manager.apps.employees.views import (EmployeesView, NewEmployeesView, EditEmployeesView,
                                                 )

urlpatterns = [
    path('', EmployeesView.as_view(), name='employees'),
    path('new', NewEmployeesView.as_view(), name='new-employee'),
    path('edit/<str:employee_uuid>', EditEmployeesView.as_view(), name='edit-employee'),
]
