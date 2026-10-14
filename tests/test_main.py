import os
import subprocess
import sys

from pwcheck import __version__


def test_module_entry_point() -> None:
    process = subprocess.run(
        [sys.executable, "-m", "pwcheck", "--version"],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert process.returncode == 0
    assert process.stdout.strip() == f"pwcheck {__version__}"


def test_module_json_stdin() -> None:
    process = subprocess.run(
        [sys.executable, "-m", "pwcheck", "--stdin", "--json"],
        input="orbit velvet canyon lantern\n",
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
        env=os.environ | {"NO_COLOR": ""},
    )
    assert process.returncode == 0
    assert '"score": 4' in process.stdout
    assert process.stderr == ""
