"""Reject inherited package paths before loading PyInstaller or cleaning outputs."""

import os
import sys
from collections.abc import Mapping
from pathlib import Path


def environment_errors(
    config_text: str, environment: Mapping[str, str]
) -> tuple[str, ...]:
    """Validate venv configuration and environment without I/O or value disclosure.

    Require exactly one explicit false setting, failing closed on missing,
    duplicate, or unrecognized configuration. A present PYTHONPATH is rejected
    even if empty; environment keys are case-insensitive on Windows.
    """
    settings: list[str] = []
    for line in config_text.splitlines():
        key, separator, value = line.partition("=")
        if separator and key.strip().casefold() == "include-system-site-packages":
            settings.append(value.strip().casefold())
    errors: list[str] = []
    if settings != ["false"]:
        errors.append(
            "Build refused: include-system-site-packages must be explicitly false "
            "in pyvenv.cfg. Recreate the isolated Python 3.14 .venv; see README."
        )
    if any(key.upper() == "PYTHONPATH" for key in environment):
        errors.append(
            "Build refused: PYTHONPATH is set. Remove it from the current process "
            "before building; see the clean-venv steps in README."
        )
    return tuple(errors)


def main() -> int:
    """Check the running interpreter's venv and report only fixed diagnostics."""
    if sys.prefix == sys.base_prefix:
        print("Build refused: use the project Python 3.14 .venv.", file=sys.stderr)
        return 1
    try:
        config = (Path(sys.prefix) / "pyvenv.cfg").read_text(encoding="utf-8")
    except OSError, UnicodeError:
        print(
            "Build refused: unable to read pyvenv.cfg. "
            "Recreate the isolated .venv; see README.",
            file=sys.stderr,
        )
        return 1
    errors = environment_errors(config, os.environ)
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
