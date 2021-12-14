import re
import socket
import ssl

import http_request
from http_request import HttpRequest


content_length_regex = re.compile(r"Content-Length[:]\s*(\d+)\r\n")
recv_buffer_size = 65536


port_by_protocol = {
    "http": 80,
    "https": 443
}


class HttpError(Exception):
    ...


def get(url: str, timeout_sec: float = 15.0):
    request = http_request.HttpRequest(url)

    return get_request(request, timeout_sec)


def get_request(http_request: HttpRequest, timeout_sec: float = 15.0) -> str:
    protocol = http_request.url.scheme or "https"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if protocol == "https":
        sock = ssl.wrap_socket(sock)

    sock.settimeout(timeout_sec)

    port = http_request.url.port or port_by_protocol[protocol]

    sock.connect((http_request.url.hostname, port))
    request_bytes = http_request.to_bytes()
    sock.sendall(request_bytes)

    # TODO: optimization
    response_headers = b''
    blankline_index = -1
    while blankline_index == -1:
        response_headers += sock.recv(recv_buffer_size)
        blankline_index = response_headers.find(b'\r\n\r\n')

    content_parts = []
    content_count = len(response_headers) - blankline_index - 4
    headers_str = response_headers.decode(encoding="utf-8")

    match = content_length_regex.search(headers_str)
    if match is None:
        raise HttpError("No Content-Length header")

    content_length = int(match.group(1))

    while content_count != content_length:
        content_part = sock.recv(recv_buffer_size)
        content_count += len(content_part)
        content_parts.append(content_part)

    return headers_str + b''.join(content_parts).decode(encoding="utf-8")


