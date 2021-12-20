from typing import Any

import utilities


class HttpMessage:
    def __init__(self, headers: dict[str, str], body: bytes):
        self.headers: dict[str, str] = headers
        self.body: bytes = body

    @staticmethod
    def get_header(headers: dict[str, str],
                   name: str,
                   default=None) -> Any:
        results = [headers.get(name, default),
                   headers.get(name.lower(), default),
                   headers.get(name.upper(), default)]

        results = list(filter(lambda v: v is not default, results))

        return results[0] if len(results) > 0 else default

    def to_bytes(self) -> bytes:
        return self.__format_headers() + self.body

    def __format_headers(self) -> bytes:
        return utilities.headers_to_str(self.headers).encode(encoding="utf-8")
