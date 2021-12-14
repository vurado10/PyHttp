import urllib.parse


class HttpRequest:
    def __init__(self, url: str):
        self.url: urllib.parse.ParseResult = urllib.parse.urlparse(url)
        self.headers = {"Host": self.url.hostname, "Content-Length": "0"}
        self.method = "GET"
        self.http_version = "1.1"
        self.__body: bytes = b''

    def to_bytes(self) -> bytes:
        return (f"{self.method} {self.url.path}?{self.url.query} "
                f"HTTP/{self.http_version}\r\n"
                .encode(encoding="utf-8")
                + self.__format_headers()
                + self.__body)

    def __format_headers(self) -> bytes:
        result_parts = []
        for name, value in self.headers.items():
            result_parts.append(f"{name}: {value}\r\n"
                                .encode(encoding="utf-8"))

        return b''.join(result_parts) + b'\r\n'
