import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
_PREFIX = ".\\.venv\\Scripts\\python.exe "
_SECTIONS = re.findall(r"^### (.+?)\n(.*?)(?=^### |^## |\Z)", README, re.M | re.S)
_EXAMPLES = [
    (name, section) for name, section in _SECTIONS if "```powershell" in section
]


def _run(command: str) -> subprocess.CompletedProcess[str]:
    source, separator, invocation = command.partition(" | ")
    if separator:
        assert source.startswith("'") and source.endswith("'")
        input_text = source[1:-1] + "\n"
    else:
        invocation = source
        input_text = None
    assert invocation.startswith(_PREFIX)
    arguments = shlex.split(invocation.removeprefix(_PREFIX))
    assert arguments[:2] == ["-m", "pwcheck"]
    existing = os.environ.get("PYTHONPATH")
    pythonpath = str(ROOT / "src")
    if existing:
        pythonpath += os.pathsep + existing
    return subprocess.run(
        [sys.executable, *arguments],
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=os.environ | {"PYTHONPATH": pythonpath, "PYTHONUTF8": "1"},
        cwd=ROOT,
        timeout=10,
        check=False,
    )


@pytest.mark.parametrize(
    ("name", "section"), _EXAMPLES, ids=[name for name, _ in _EXAMPLES]
)
def test_readme_usage_output(name: str, section: str) -> None:
    commands = re.findall(r"```powershell\n(.*?)\n```", section, re.S)
    assert len(commands) == 1
    expected = re.findall(r"```(?:text|json)\n(.*?)\n```", section, re.S)
    exit_code = re.search(r"Exit code: \*\*([012])\*\*", section)
    assert exit_code is not None
    process = _run(commands[0])
    assert process.returncode == int(exit_code[1]), name
    assert process.stdout.rstrip("\n") in expected
    if process.stderr:
        assert process.stderr.rstrip("\n") in expected
    else:
        assert len(expected) == 1


def test_all_readme_usage_examples_are_checked() -> None:
    assert len(_EXAMPLES) == 7
    assert {name.split(".")[0] for name, _ in _EXAMPLES} == {
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "JSON example",
    }


def test_readme_version_output() -> None:
    installation = README.split("## Installation", 1)[1].split("## Why this exists", 1)[
        0
    ]
    expected = re.findall(r"```text\n(.*?)\n```", installation, re.S)
    process = _run(_PREFIX + "-m pwcheck --version")
    assert process.returncode == 0
    assert process.stdout.rstrip("\n") in expected
    assert process.stderr == ""
