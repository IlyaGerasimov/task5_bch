import argparse
from gen import gen
from code import code
from decode import decode


def parse_init():
    parser = argparse.ArgumentParser(description='Code')
    parser.add_argument(
        '-g', '--generate',
        action='store_true',
        help='Mode for generation process.'
    )
    parser.add_argument(
        '-n',
        nargs='?',
        type=int,
        default=None,
        help="Desirable max length of the message block."
    )
    parser.add_argument(
        '-p', '--probability',
        nargs='?',
        type=float,
        default=None,
        help="Error probability."
    )
    parser.add_argument(
        '-c', '--code',
        action='store_true',
        help='Mode for coding process.'
    )
    parser.add_argument(
        '-f', '--file',
        nargs="?",
        type=argparse.FileType('r'),
        help="File with code description."
    )
    parser.add_argument(
        '-y',
        nargs='?',
        type=argparse.FileType('r'),
        help="File with message for decoding."
    )
    parser.add_argument(
        '-d', '--decode',
        action='store_true',
        help='Mode for decoding.'
    )
    args = parser.parse_args()
    if args.generate:
        if args.n and args.probability:
            return args, 1
        else:
            exit("There is '-g' flag but no parameters.")
    if args.code:
        if args.file:
            return args, 2
        else:
            exit("There is '-c' flag but no parameters.")
    if args.decode:
        if args.file and args.y:
            return args, 3
        else:
            exit("There is '-d' flag but no parameters.")
    exit("There is no mode flag.")


if __name__ == "__main__":
    args, mode = parse_init()
    if mode == 1:
        gen(args.n, args.probability)
    elif mode == 2:
        code(args.file)
    elif mode == 3:
        decode(args.file, args.y)

