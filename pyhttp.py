import argparse
from send_recv_helpers import send_recv_with_redirect, send_recv


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

    output = None
    if args.output is not None:
        output = open(args.output, "wb")

    def conf_write(data) -> None:
        if output is None:
            print(data)
            return

        if type(data) != bytes and type(data) != bytearray:
            raise ValueError("Can't write non bytes data")

        output.write(data)


    if args.redirect:
        request, response = send_recv_with_redirect(args)
    else:
        requests, response = send_recv(args)

    print()
    if args.aheaders:
        conf_write(response.status_line.encode(encoding="utf-8"))
        conf_write(response.headers_str.encode(encoding="utf-8"))

    if not args.nbody:
        conf_write(response.body_bytes)
