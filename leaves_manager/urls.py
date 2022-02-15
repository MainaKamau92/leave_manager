"""leaves_manager URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('leaves_manager.apps.accounts.urls')),
    path('organization/', include('leaves_manager.apps.organization.urls')),
    path('time-off/', include('leaves_manager.apps.leaves.urls')),
    path('employees/', include('leaves_manager.apps.employees.urls')),
    path('reports/', include('leaves_manager.apps.reports.urls')),
    # path('errors/', include('leaves_manager.apps.error_pages.urls')),
]

handler404 = 'leaves_manager.apps.error_pages.views.page_not_found'
handler500 = 'leaves_manager.apps.error_pages.views.internal_server_error'
handler400 = 'leaves_manager.apps.error_pages.views.bad_request_error'
handler403 = 'leaves_manager.apps.error_pages.views.forbidden_request_error'
