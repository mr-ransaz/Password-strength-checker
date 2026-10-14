"""Allow invocation with python -m pwcheck."""

from pwcheck.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
