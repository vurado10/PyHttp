import argparse
import itertools
import re
import sys

import http_client

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
                        type=float, default=0.0,
                        help="timeout in seconds")
    # parser.add_argument("--method", default="get")

    # add_arguments_with_list_value(parser,
    #                               "--headers")

    return transform_values(vars(parser.parse_args(args)))


if __name__ == "__main__":
    args = parse_argumets(sys.argv[1:])
    url = args["url"]
    timeout = args["timeout"]
    output = args["output"]
    responce = http_client.get(url, timeout_sec=timeout)
    if output is not None:
        print(responce, file=open(output, "w"))
    else:
        print(responce)
