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

    @staticmethod
    def validate_method_name(name: str) -> str:
        if name not in HttpRequest.valid_methods:
            raise ValueError(f"Method {name} isn't supported")

        return name

    @staticmethod
    def validate_path(uri: str) -> str:
        return uri

    def to_bytes(self) -> bytes:
        start_str = f"{self.method} {self.path}"
        start_str += "?" + urllib.parse.quote(self.query) if self.query else ""
        start_str += f" HTTP/{self.http_version}\r\n"

        return start_str.encode(encoding="utf-8") + self.message.to_bytes()


