from functools import wraps
from django.http import HttpResponse

"""
Хэлперы для быстрого добавления cors-заголовков.
Использование:

    @cors_wide_open
    def view(request):
        blabla

"""


ACCESS_CONTROL_ALLOW_ORIGIN = 'Access-Control-Allow-Origin'
ACCESS_CONTROL_EXPOSE_HEADERS = 'Access-Control-Expose-Headers'
ACCESS_CONTROL_ALLOW_CREDENTIALS = 'Access-Control-Allow-Credentials'
ACCESS_CONTROL_ALLOW_HEADERS = 'Access-Control-Allow-Headers'
ACCESS_CONTROL_ALLOW_METHODS = 'Access-Control-Allow-Methods'
ACCESS_CONTROL_MAX_AGE = 'Access-Control-Max-Age'


WIDE_OPEN_CORS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Allow-Headers': 'content-type,accept-encoding',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
}


def add_response_headers(response, headers):
    if headers:
        for k, v in headers.items():
            response[k] = v
        return response


def add_cors_headers(headers):
    def wrapper(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.method == 'OPTIONS':
                response = HttpResponse()
            else:
                response = view(request, *args, **kwargs)

            add_response_headers(response, headers)

            return response
        return wrapped
    return wrapper


def cors_wide_open(f):
    return add_cors_headers(WIDE_OPEN_CORS)(f)
