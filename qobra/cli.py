"""Command line interface: python -m qobra program.qbr [-o OUTPUT]"""

import argparse
import sys

from . import compile_source


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="qobra",
        description="Compile a Qobra program to EWVM assembly.",
    )
    ap.add_argument("source", help="path to the Qobra source file (.qbr)")
    ap.add_argument("-o", "--output", metavar="FILE",
                    help="write the generated code to FILE instead of stdout")
    args = ap.parse_args(argv)

    try:
        with open(args.source, encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        print(f"[Error] Cannot read '{args.source}': {e.strerror}.", file=sys.stderr)
        return 1

    code = compile_source(text)  # exits with status 1 on a compile error
    output = "\n".join(code) + "\n"

    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as f:
            f.write(output)
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
