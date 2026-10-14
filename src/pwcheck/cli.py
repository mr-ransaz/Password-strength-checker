"""Argument parsing and I/O for the pwcheck command."""

import argparse
import getpass
import os
import sys
import warnings
from collections.abc import Sequence

from pwcheck import __version__
from pwcheck.analyzer import analyze_password
from pwcheck.hibp import check_password
from pwcheck.report import format_human, format_json

MAX_PASSWORD_LENGTH = 4096


class _SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        # argparse normally echoes unknown arguments, which may be passwords.
        super().error("Invalid command-line arguments. Use --help for usage.")


def build_parser() -> argparse.ArgumentParser:
    """Build a parser with mutually exclusive password input methods."""
    parser = _SafeArgumentParser(
        prog="pwcheck",
        description="Estimate password strength; secure no-echo input is the default.",
        allow_abbrev=False,
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--password",
        metavar="TEXT",
        help="discouraged: visible in history/process arguments",
    )
    source.add_argument(
        "--stdin", action="store_true", help="read one password from standard input"
    )
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    parser.add_argument(
        "--hibp", action="store_true", help="opt in to a HIBP hash-prefix network check"
    )
    parser.add_argument(
        "--context",
        default="",
        metavar="TOKENS",
        help="comma-separated names, years, or places",
    )
    parser.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    parser.add_argument("--version", action="version", version=f"pwcheck {__version__}")
    return parser


def _read_password(arguments: argparse.Namespace) -> str:
    if arguments.password is not None:
        print(
            "Warning: --password exposes the password to shell history and process "
            "arguments. Use the secure prompt instead.",
            file=sys.stderr,
        )
        password = arguments.password
    elif arguments.stdin:
        password = sys.stdin.read(MAX_PASSWORD_LENGTH + 3)
        # Preserve spaces and remove at most one transport line ending.
        if password.endswith("\r\n"):
            password = password[:-2]
        elif password.endswith("\n"):
            password = password[:-1]
        if "\n" in password or "\r" in password:
            raise ValueError("Expected a single password line on stdin.")
    else:
        # Refuse getpass's echoing fallback if a secure terminal is unavailable.
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            password = getpass.getpass("Password: ")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password exceeds the 4096-character CLI limit.")
    return password


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return 0 (good/strong), 1 (weak), or 2 (error)."""
    arguments = build_parser().parse_args(argv)
    try:
        password = _read_password(arguments)
        context = tuple(
            token.strip() for token in arguments.context.split(",") if token.strip()
        )
        result = analyze_password(password, context)
        breach = check_password(password) if arguments.hibp else None
        if breach is not None and breach.status == "found":
            result = analyze_password(password, context, breached=True)
        color = (
            sys.stdout.isatty()
            and "NO_COLOR" not in os.environ
            and not arguments.no_color
        )
        output = (
            format_json(result, breach)
            if arguments.json
            else format_human(result, color=color, breach=breach)
        )
        print(output, flush=True)
        if breach is not None and breach.status == "unavailable":
            return 2
        return 0 if result.score >= 3 else 1
    except EOFError, getpass.GetPassWarning:
        print(
            "Error: secure input unavailable; use --stdin with a trusted source.",
            file=sys.stderr,
        )
    except KeyboardInterrupt:
        print("Error: input cancelled.", file=sys.stderr)
    except OSError, UnicodeError, ValueError:
        # Do not interpolate exception text: it could contain secret input.
        print(
            "Error: unable to process input or output "
            "(one line; maximum 4096 characters).",
            file=sys.stderr,
        )
    return 2
