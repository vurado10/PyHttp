import argparse
import base64
import itertools
import socket
import urllib.parse
import http_client
from http_message import HttpMessage
from http_request import HttpRequest


def prepare_body(body: str) -> bytes:
    return urllib.parse.quote(body, safe="&=").encode(encoding="utf-8")


def prepare_headers(headers_list: list) -> dict[str, str]:
    result = {}
    for header_str in itertools.chain(*headers_list):
        key, value = map(lambda s: s.strip(), header_str.split(":"))
        result[key] = value

    return result


def prepare_cookies(cookies_list: list) -> str:
    return ";".join(itertools.chain(*cookies_list))


def prepare_basic_auth_data(username: str, password: str) -> str:
    return ("Basic "
            + base64
            .b64encode(f"{username}:{password}".encode(encoding="utf-8"))
            .decode(encoding="utf-8"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="pyhttp")
    parser.add_argument("url")
    parser.add_argument("-o", "--output")
    parser.add_argument("-t", "--timeout",
                        type=float, default=None,
                        help="timeout in seconds")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--headers", action="append", nargs="+", default=[])
    parser.add_argument("--cookies", action="append", nargs="+", default=[])
    parser.add_argument("--body", default="")
    parser.add_argument("-r", "--redirect", action="store_true")
    parser.add_argument("--aheaders", action="store_true")
    parser.add_argument("--nbody", action="store_true")
    parser.add_argument("--srq", action="store_true", help="show sent request")
    parser.add_argument("-u", "--username")
    parser.add_argument("-p", "--password")
    args = parser.parse_args()


    client = http_client.HttpClient(args.url, args.timeout)
    try:
        client.connect()
    except socket.gaierror as e:
        print(e)
        exit(1)

    message = HttpMessage(prepare_headers(args.headers),
                          prepare_body(args.body))

    if args.body:
        message.headers["Content-Type"] = "application/x-www-form-urlencoded"

    if args.cookies:
        message.headers["Cookie"] = prepare_cookies(args.cookies)

    if args.username is not None and args.password is not None:
        message.headers["Authorization"] = \
            prepare_basic_auth_data(args.username, args.password)


    request = HttpRequest(args.method.upper(), "", "", message)

    sent_request = client.send_request(request)

    if args.srq:
        print(sent_request)

    response = None
    try:
        response = client.get_response()
    except socket.timeout:
        print("#####TIMEOUT#####")
        exit(1)

    answer_text_parts = []
    if args.aheaders:
        answer_text_parts.append(response.status_line)
        answer_text_parts.append(response.headers_str)

    if not args.nbody:
        answer_text_parts.append(response.body)

    answer_text = "".join(answer_text_parts)

    print()
    if args.output is not None:
        print(answer_text, file=open(args.output, "w"))
    else:
        print(answer_text)
