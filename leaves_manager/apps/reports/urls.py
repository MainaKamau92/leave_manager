from django.urls import path

from . import views

urlpatterns = [
    path('', views.time_off_request_list, name='reports')
]
