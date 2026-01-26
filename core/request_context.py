import threading

_request_local = threading.local()


def get_current_request():
    """Get the current request from thread-local storage."""
    return getattr(_request_local, "request", None)


class RequestContextMiddleware:
    """
    Middleware to store the current request in thread-local storage.
    This allows accessing the request anywhere without passing it explicitly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _request_local.request = request
        try:
            response = self.get_response(request)
        finally:
            # Clean up after request is done
            _request_local.request = None
        return response
