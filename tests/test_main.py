import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pwcheck import __version__


def _source_environment() -> dict[str, str]:
    source = str(Path(__file__).resolve().parents[1] / "src")
    existing = os.environ.get("PYTHONPATH")
    pythonpath = source + os.pathsep + existing if existing else source
    return os.environ | {"PYTHONPATH": pythonpath}


@pytest.mark.parametrize(
    "site_flags", [[], ["-S"]], ids=["default", "no-site-packages"]
)
def test_module_entry_point(site_flags: list[str]) -> None:
    process = subprocess.run(
        [sys.executable, *site_flags, "-m", "pwcheck", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
        env=_source_environment(),
        cwd=Path(__file__).resolve().parent,
    )
    assert process.returncode == 0
    assert process.stdout.strip() == f"pwcheck {__version__}"
    assert process.stderr == ""


@pytest.mark.parametrize(
    "site_flags", [[], ["-S"]], ids=["default", "no-site-packages"]
)
def test_module_json_stdin(site_flags: list[str]) -> None:
    process = subprocess.run(
        [sys.executable, *site_flags, "-m", "pwcheck", "--stdin", "--json"],
        input="orbit velvet canyon lantern\n",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
        env=_source_environment() | {"NO_COLOR": ""},
        cwd=Path(__file__).resolve().parent,
    )
    assert process.returncode == 0
    assert json.loads(process.stdout)["score"] == 4
    assert process.stderr == ""


def test_source_environment_prepends_existing_pythonpath(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = os.pathsep.join(["existing-a", "existing-b"])
    monkeypatch.setenv("PYTHONPATH", existing)
    monkeypatch.setenv("PWCHECK_TEST_VALUE", "preserved")
    environment = _source_environment()
    assert environment["PYTHONPATH"].split(os.pathsep) == [
        str(Path(__file__).resolve().parents[1] / "src"),
        "existing-a",
        "existing-b",
    ]
    assert environment["PWCHECK_TEST_VALUE"] == "preserved"
