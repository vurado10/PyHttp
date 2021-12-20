import socket
from collections import Callable

from http_response import HttpResponse

handler_by_status_code_and_http_version = {}


def get_handler(http_version: str,
                status_code: int) -> Callable[[socket.socket], HttpResponse]:
    return handler_by_status_code_and_http_version[(http_version, status_code)]


def response_handler(http_version: str, status_code: int):
    def decorator(func):
        handler_by_status_code_and_http_version[
            (http_version, status_code)] = func

        return func

    return decorator


@response_handler("1.1", 200)
def handle_200(sock: socket.socket) -> HttpResponse:
    ...
