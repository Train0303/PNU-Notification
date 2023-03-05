import logging
import sys
import time
import traceback

from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseServerError

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        log_data = {
            "remote_address": request.META['REMOTE_ADDR'],
            "user_email": request.user.email if request.user.is_authenticated else "anonymous",
            "request_method": request.method,
            "request_path": request.get_full_path(),
            "query_params": dict(request.GET.items()),
        }

        response = self.get_response(request)
        response_time = f'{round(time.time() - start_time, 2)}s'
        log_data["status_code"] = response.status_code
        log_data["response_time"] = response_time

        logger.info(msg=log_data)

        if str(response.status_code).startswith('5'):
            error_message = 'Internal Server Error'
            error_type, error_value, traceback_obj = sys.exc_info()
            subject = f'Server Error'
            message = f"{error_message}\n\n{request.build_absolute_uri()}"
            message += f"Error Type: {error_type}\n"
            message += f"Error Value: {error_value}\n"
            message += f"Traceback:\n\n{traceback.format_tb(traceback_obj)}"
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_ADMIN],
                fail_silently=False,
            )
            return HttpResponseServerError(error_message)

        return response