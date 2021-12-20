import urllib.parse

import utilities
from http_message import HttpMessage


class HttpRequest:
    valid_methods = {"GET", "POST"}

    def __init__(self,
                 method: str,
                 path: str,
                 query: str,
                 message: HttpMessage,
                 http_version="1.1"):
        self.method = HttpRequest.validate_method_name(method)
        self.path = HttpRequest.validate_path(path)
        self.query = query
        self.message = message
        self.http_version = http_version

    @property
    def start_line(self) -> str:
        start_str = f"{self.method} {self.path}"
        start_str += "?" + urllib.parse.quote(self.query, safe='=&') \
            if self.query \
            else ""
        start_str += f" HTTP/{self.http_version}\r\n"

        return start_str

    @property
    def headers_str(self) -> str:
        return utilities.headers_to_str(self.message.headers)

    @property
    def body(self) -> str:
        return self.message.body.decode(encoding="utf-8", errors="ignore")

    def __str__(self) -> str:
        return self.start_line + self.headers_str + self.body

    @staticmethod
    def validate_method_name(name: str) -> str:
        if name not in HttpRequest.valid_methods:
            raise ValueError(f"Method {name} isn't supported")

        return name

    @staticmethod
    def validate_path(uri: str) -> str:
        return uri

    def to_bytes(self) -> bytes:
        return self.start_line.encode(encoding="utf-8") \
               + self.message.to_bytes()


