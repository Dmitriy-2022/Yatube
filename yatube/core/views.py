from django.shortcuts import render


def page_not_found_404(request, exception):
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure_403(request, reason=''):
    return render(request, 'core/403.html')


def internal_server_error_500(request, reason=''):
    return render(request, 'core/500.html')
