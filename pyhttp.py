import argparse
import base64
import itertools
import re
import socket
import urllib.parse
import http_client
from http_message import HttpMessage
from http_request import HttpRequest

key_value_pair_regex = re.compile(r" *([\w-]+) *[,:=]+?\s*(.*)")

key_value_lists_names = ["cookies", "headers"]


def add_arguments_with_list_value(parser, *names) -> None:
    for name in names:
        parser.add_argument(name,
                            action="append",
                            nargs="+")


def convert_to_key_value_pairs(raw_pairs: list[str]) -> list[tuple[str, ...]]:
    result = []
    for s in itertools.chain.from_iterable(raw_pairs):
        match = key_value_pair_regex.match(s)
        if not match:
            return list(itertools.chain.from_iterable(raw_pairs))

        result.append(tuple(match.groups()))

    return result


def transform_values(dictionary: dict) -> dict:
    for key in dictionary.keys():
        value = dictionary[key]
        if key in key_value_lists_names:
            dictionary[key] = convert_to_key_value_pairs(value)

    return dictionary


def parse_argumets(args: list[str]) -> dict:
    parser = argparse.ArgumentParser(prog="pyhttp")
    parser.add_argument("url")
    parser.add_argument("-o", "--output")
    parser.add_argument("-t", "--timeout",
                        type=float, default=None,
                        help="timeout in seconds")
    parser.add_argument("--method", default="GET")

    # add_arguments_with_list_value(parser,
    #                               "--headers")

    return transform_values(vars(parser.parse_args(args)))


def prepare_body(body: str) -> bytes:
    return urllib.parse.quote(body).encode(encoding="utf-8")


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
    parser.add_argument("--headers", action="append", default=[])
    parser.add_argument("--cookies", action="append", default=[])
    parser.add_argument("--body", default="")
    parser.add_argument("-r", "--redirect", action="store_true")
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

    message.headers["Cookie"] = prepare_cookies(args.cookies)

    if args.username is not None and args.password is not None:
        message.headers["Authorization"] = \
            prepare_basic_auth_data(args.username, args.password)


    request = HttpRequest(args.method.upper(), "", "", message)

    client.send_request(request)

    response = client.get_response()

    print()

    if args.output is not None:
        print(response, file=open(args.output, "w"))
    else:
        print(response)
