import socket
import ssl
import urllib.parse
import utilities
from typing import Optional
from http_message import HttpMessage
from http_request import HttpRequest
from http_response import HttpResponse


class HttpClient:
    port_by_protocol = {
        "http": 80,
        "https": 443
    }

    def __init__(self,
                 url: str,
                 operations_timeout_sec: Optional[float] = None):
        self.url: urllib.parse.ParseResult = urllib.parse.urlparse(url)
        self.protocol = self.url.scheme or "https"
        self.port = self.url.port or HttpClient.port_by_protocol[self.protocol]
        self.socket: Optional[socket.socket] = None
        self.timeout_sec = operations_timeout_sec

    def connect(self):
        if self.socket is not None:
            raise RuntimeError("Already connected")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.protocol == "https":
            self.socket = ssl.wrap_socket(self.socket)

        self.socket.settimeout(self.timeout_sec)

        self.socket.connect((self.url.hostname, self.port))

    def close(self):
        self.socket.close()

    def send_request(self, request: HttpRequest) -> HttpRequest:
        request.path = self.url.path if self.url.path else "/"
        request.query = self.url.query

        if float(request.http_version) >= 1.1:
            request.message.headers["Host"] = self.url.hostname

        request.message.headers["Content-Length"] = \
            str(len(request.message.body))

        self.socket.sendall(request.to_bytes())

        return request

    def get_response(self) -> HttpResponse:
        headers, content = self.recv_status_and_headers()

        response = \
            utilities.parse_status_and_headers_to_http_response(headers)

        response.message.body = self.recv_content(response.message.headers,
                                                  content)

        return response

    def recv_status_and_headers(self) -> tuple[str, bytes]:
        response_headers = bytes()
        blankline_index = -1
        while blankline_index == -1:
            # TODO: more bytes in buffer
            response_headers += self.socket.recv(1000)
            blankline_index = response_headers.find(b'\r\n\r\n')

        headers_str = response_headers[:blankline_index + 4] \
            .decode(encoding="utf-8")
        content = response_headers[blankline_index + 4:]

        return headers_str, content

    def recv_content(self,
                     headers: dict[str, str],
                     start_content: bytes) -> bytes:
        content_length_str = HttpMessage.get_header(headers, "Content-Length")
        if content_length_str is not None:
            content_length = int(content_length_str)
            utilities.update_progress_bar(content_length, len(start_content))

            return start_content + utilities.recv_all(
                self.socket,
                int(content_length_str) - len(start_content),
                lambda mx, cr:
                utilities.update_progress_bar(content_length,
                                              len(start_content) + cr))

        transfer_encoding = HttpMessage.get_header(headers,
                                                   "Transfer-Encoding")

        if transfer_encoding is None:
            raise RuntimeError("No transfer-encoding")

        if transfer_encoding.lower() == "chunked":
            return utilities.recv_chunked_content(self.socket, start_content)

        raise RuntimeError(f"Can't parse body "
                           f"transfer-encoding: {transfer_encoding}")
