import re
import socket
import urllib.parse
from typing import Callable, Generator
from http_message import HttpMessage
from http_response import HttpResponse

status_regex = re.compile(r"HTTP/([.\d]+) (\d+) (.+)")
header_regex = re.compile(r"([\w-]+):(.+)")


def convert_dict_to_perc_encoding(d: dict[str, str]) -> str:
    result_parts = []

    for key, value in d.items():
        result_parts.append(key + "=" + value)

    return urllib.parse.quote('&'.join(result_parts), safe="&=")


def parse_status_and_headers_to_http_response(data: str) \
        -> HttpResponse:
    status_and_headers = data.strip().split("\r\n")

    groups = status_regex.match(status_and_headers[0]).groups()

    result = HttpResponse(groups[0],
                          int(groups[1]),
                          groups[2],
                          HttpMessage({}, b''))

    headers = {}
    for header_str in status_and_headers[1:]:
        key, value = map(lambda s: s.strip(),
                         header_regex.match(header_str).groups())
        headers[key] = value

    result.message.headers = headers

    return result


def update_progress_bar(max_value: int, current_value: int) -> None:
    if max_value == 0:
        print("\r" + "0/0", end="")
        return

    progress = int(current_value / max_value * 100)

    print("\r" + "#" * progress + " " * (100 - progress)
          + f" {current_value}/{max_value}", end="")
    # time.sleep(0.5)


def recv_all(sock: socket.socket,
             count: int,
             progress_callback: Callable[[int, int], None] = None) -> bytes:
    result = b''
    result_count = 0

    while result_count != count:
        result_part = sock.recv(count - result_count)
        result_count += len(result_part)
        result += result_part

        if progress_callback is None:
            continue

        progress_callback(count, result_count)

    return result


def get_next_byte(sock: socket.socket,
                  start_content: bytes,
                  buffer_len: int = 1024) -> Generator[int, None, None]:
    buffer = start_content if len(start_content) > 0 else sock.recv(buffer_len)

    i = 0
    while True:
        yield buffer[i]

        i += 1
        if i == len(buffer):
            buffer = sock.recv(buffer_len)
            i = 0


def get_chunks(sock: socket.socket,
               start_content: bytes) -> Generator[bytes, None, None]:
    chunk = bytearray()

    is_length = True
    length_token = bytearray()
    length = -1
    is_potential_line_end = False

    for bt in get_next_byte(sock, start_content):
        if is_length:
            if is_potential_line_end:
                if bt == 10:  # \n
                    length = int(length_token.decode(encoding="utf-8"), 16)
                    length_token = bytearray()
                    if length == 0:
                        break

                    is_length = False
                else:
                    length_token.append(13)
                    length_token.append(bt)

                is_potential_line_end = False
                continue

            if bt == 13:  # \r
                is_potential_line_end = True
                continue

            length_token.append(bt)
            continue

        chunk.append(bt)

        if len(chunk) == length + 2:
            yield chunk[:-2]
            chunk = bytearray()
            is_length = True


def recv_chunked_content(sock: socket.socket,
                         start_content: bytes) -> bytes:
    return b''.join(get_chunks(sock, start_content))


def headers_to_str(headers: dict[str, str]) -> str:
    result_parts = []
    for name, value in headers.items():
        result_parts.append(f"{name}: {value}")

    return "\r\n".join(result_parts) + "\r\n\r\n"
