from django.shortcuts import redirect

class RoleRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin_dashboard_app-dashboard/') and request.user.is_authenticated:
            if request.user.role != 'ADMIN':
                return redirect('login')
        return self.get_response(request)
