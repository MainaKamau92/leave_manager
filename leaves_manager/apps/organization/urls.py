from django.urls import path

from . import views

urlpatterns = [
    path('new-organization/', views.new_organization, name='new-organization')
]
