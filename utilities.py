import re
import socket
import time
import urllib.parse
from typing import Callable, Generator, Iterable

import environment
from http_message import HttpMessage
from http_response import HttpResponse

status_regex = re.compile(r"HTTP/([.\d]+) (\d+) (.*)")
header_regex = re.compile(r"\s*([\w-]+):(.+)")


def convert_dict_to_perc_encoding(d: dict[str, str]) -> str:
    result_parts = []

    for key, value in d.items():
        result_parts.append(key + "=" + value)

    return urllib.parse.quote('&'.join(result_parts), safe="&=")


def parse_status_and_headers_to_http_response(data: str) \
        -> HttpResponse:
    status_and_headers = data.strip().split("\r\n")

    match = status_regex.match(status_and_headers[0])
    if match is None:
        print("ERROR: Can't parse status line")
        print(status_and_headers)
        exit(1)

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

    time.sleep(environment.PAUSE_AFTER_PROGRESS_BAR_UPDATE)


def recv_all(sock: socket.socket,
             length: int,
             progress_callback: Callable[[int, int], None] = None,
             part_length: int = 1024) -> Iterable[bytes]:
    result_length = 0

    while result_length != length:
        result_part = sock.recv(part_length)
        result_length += len(result_part)

        if progress_callback is None:
            continue

        progress_callback(length, result_length)

        yield result_part


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


def get_chunked_content(sock: socket.socket,
                        start_content: bytes,
                        buffer_size: int = 1024) \
        -> Generator[bytes, None, None]:
    buffer = bytearray()

    is_length = True
    length_token = bytearray()
    length = -1
    chunk_current_lenght = 0
    is_potential_line_end = False
    is_chunk_separator = False
    chunk_separator_length = 0

    for bt in get_next_byte(sock, start_content):
        if is_chunk_separator:
            chunk_separator_length += 1
            if chunk_separator_length == 2:
                is_chunk_separator = False
            continue
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

        buffer.append(bt)
        chunk_current_lenght += 1

        if len(buffer) == buffer_size:
            yield buffer
            buffer = bytearray()

        if chunk_current_lenght == length:
            chunk_separator_length = 0
            chunk_current_lenght = 0
            is_chunk_separator = True
            is_length = True

    if len(buffer) > 0:
        yield buffer



def recv_chunked_content(sock: socket.socket,
                         start_content: bytes) -> Iterable[bytes]:
    return get_chunked_content(sock, start_content)


def headers_to_str(headers: dict[str, str]) -> str:
    result_parts = []
    for name, value in headers.items():
        result_parts.append(f"{name}: {value}")

    return "\r\n".join(result_parts) + "\r\n\r\n"
