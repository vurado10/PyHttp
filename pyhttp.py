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


    if args.redirect:
        request, response = send_recv_with_redirect(args)
    else:
        requests, response = send_recv(args)

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
