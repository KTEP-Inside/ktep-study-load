from django.core.exceptions import PermissionDenied

from .views import page_access_is_denied


class PermissionDeniedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    @staticmethod
    def process_exception(request, exception):
        if isinstance(exception, PermissionDenied):
            return page_access_is_denied(request)
        return None
