import argparse
import base64
import itertools
import socket
import urllib.parse
import http_client
from http_error import HttpError
from http_message import HttpMessage
from http_request import HttpRequest
from http_response import HttpResponse


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


def send_recv_with_redirect(args: argparse.Namespace) \
        -> tuple[http_client.HttpClient, HttpRequest, HttpResponse]:
    client, request, response = send_recv(args)

    while response.status_code in [301, 302, 303, 307, 308]:
        url = urllib.parse.urlparse(args.url)
        location = response.message.headers["Location"].strip()
        if location[0] == '/':
            args.url = f"{url.scheme}://{url.netloc}{location}"
        elif location[0] == 'h':
            args.url = location
        else:
            raise HttpError("Incorrect url of redirecting")

        print()
        print("Redirect to " + args.url)
        client.close()
        client, request, response = send_recv(args)

    return client, request, response


def send_recv(args: argparse.Namespace) -> tuple[http_client.HttpClient,
                                                 HttpRequest,
                                                 HttpResponse]:
    client = http_client.HttpClient(args.url, args.timeout)
    try:
        client.connect()
    except socket.gaierror as e:
        print(e)
        exit(1)
    except ConnectionRefusedError:
        print("ERROR: Connection refused")
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

    request = None
    try:
        request = HttpRequest(args.method.upper(), "", "", message)
    except ValueError as e:
        print(e)
        exit(1)

    sent_request = client.send_request(request)

    if args.srq:
        print(sent_request)

    response = None
    try:
        response = client.get_response()
    except socket.timeout:
        print("#####TIMEOUT#####")
        exit(1)

    return client, sent_request, response
