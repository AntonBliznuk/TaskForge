import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class TimerMiddleware(MiddlewareMixin):
    """
    Middleware for measuring HTTP request execution time and logging the result.
    """
    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"{request.path} took {duration:.3f} seconds ⤵")
        return response