"""
Middleware to log `*/api/*` requests and responses.
"""
from django.http import HttpResponse


class HealthCheckMiddleware:
    """Request Logging Middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/hc':
            return HttpResponse("server is healthy")
        response = self.get_response(request)
        return response
