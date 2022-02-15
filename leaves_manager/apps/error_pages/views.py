# Create your views here.
from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, 'error_pages/404.html', status=404)


def internal_server_error(request):
    return render(request, 'error_pages/500.html', status=500)


def bad_request_error(request, exception):
    return render(request, 'error_pages/400.html', status=400)


def forbidden_request_error(request, exception, *args, **argv):
    return render(request, 'error_pages/403.html', status=403)

# def my_test_500_view(request):
#     # Return an "Internal Server Error" 500 response code.
#     # PermissionError
#     raise SuspiciousOperation('Make response code 400!')
