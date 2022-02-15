from django.urls import path

from leaves_manager.apps.leaves.views import (TimeOffRequestsView, NewTimeOffRequestsView,
                                              EditTimeOffRequestView, NewTimeOffTypeView, EditTimeOffTypeView,
                                              NewCustomHolidayView, EditCustomHolidayView, HolidaysView,
                                              TimeOffTypesView)

urlpatterns = [
    path('requests/', TimeOffRequestsView.as_view(), name='requests'),
    path('time-off-types/', TimeOffTypesView.as_view(), name='time-off-types'),
    path('new/', NewTimeOffRequestsView.as_view(), name='new-request'),
    path('edit/<str:time_off_request_uuid>', EditTimeOffRequestView.as_view(), name='edit-request'),
    path('type/new/', NewTimeOffTypeView.as_view(), name='time-off-type'),
    path('type/edit/<str:time_off_type_uuid>', EditTimeOffTypeView.as_view(), name='edit-type'),
    path('custom-holidays/new/', NewCustomHolidayView.as_view(), name='custom-holiday'),
    path('custom-holidays/edit/<str:custom_holiday_uuid>', EditCustomHolidayView.as_view(), name='edit-custom-holiday'),
    path('holidays/', HolidaysView.as_view(), name='holidays'),
]
