import logging
import time

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

        return response