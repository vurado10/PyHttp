import utilities
from http_message import HttpMessage


class HttpResponse:
    def __init__(self,
                 http_version: str,
                 status_code: int,
                 descr: str,
                 message: HttpMessage):
        self.http_version = http_version
        self.status_code = status_code
        self.descr = descr
        self.message = message


    def __str__(self) -> str:
        return self.status_line + self.headers_str + self.content


    @property
    def status_line(self) -> str:
        return f"HTTP/{self.http_version} {self.status_code} {self.descr}\r\n"

    @property
    def headers_str(self) -> str:
        return utilities.headers_to_str(self.message.headers)

    @property
    def content(self) -> str:
        return self.message.body.decode(encoding="utf-8", errors="ignore")

    @property
    def content_bytes(self) -> bytes:
        return self.message.body
