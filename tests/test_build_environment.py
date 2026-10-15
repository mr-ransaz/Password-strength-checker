import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import build_environment

ISOLATED = (
    "home = interpreter\ninclude-system-site-packages = false\nversion = 3.14.0\n"
)


@pytest.mark.parametrize(
    "config",
    [ISOLATED, " INCLUDE-SYSTEM-SITE-PACKAGES = FALSE \r\n", "# comment\n" + ISOLATED],
)
def test_isolated_configuration_is_accepted(config: str) -> None:
    assert build_environment.environment_errors(config, {"PATH": "unchanged"}) == ()


@pytest.mark.parametrize(
    "setting",
    ["true", "TRUE", " true ", "yes", "", "0"],
)
def test_inherited_or_unrecognized_configuration_is_rejected(setting: str) -> None:
    errors = build_environment.environment_errors(
        f"include-system-site-packages = {setting}\n", {}
    )
    assert len(errors) == 1
    assert "include-system-site-packages must be explicitly false" in errors[0]


@pytest.mark.parametrize(
    "config",
    [
        "",
        "home = interpreter\n",
        ISOLATED + "include-system-site-packages = true\n",
        ISOLATED + "include-system-site-packages = false\n",
    ],
)
def test_missing_or_duplicate_settings_fail_closed(config: str) -> None:
    assert build_environment.environment_errors(config, {})


@pytest.mark.parametrize("key", ["PYTHONPATH", "pythonpath", "PythonPath"])
@pytest.mark.parametrize("value", ["", " ", "private-sentinel-path"])
def test_any_set_pythonpath_is_rejected_without_disclosure(
    key: str, value: str
) -> None:
    errors = build_environment.environment_errors(ISOLATED, {key: value})
    assert len(errors) == 1
    assert "PYTHONPATH is set" in errors[0]
    assert "private-sentinel-path" not in errors[0]


def test_both_errors_and_input_immutability() -> None:
    environment = {"PYTHONPATH": "private-sentinel-path", "OTHER": "preserved"}
    original = environment.copy()
    errors = build_environment.environment_errors(
        "include-system-site-packages = true\n", environment
    )
    assert len(errors) == 2
    assert environment == original
    assert "private-sentinel-path" not in "\n".join(errors)


def test_unrelated_environment_keys_are_allowed() -> None:
    assert (
        build_environment.environment_errors(
            ISOLATED, {"PYTHONPATH_BACKUP": "allowed", "PYTHONUNBUFFERED": "1"}
        )
        == ()
    )


def _fake_interpreter(monkeypatch: pytest.MonkeyPatch, prefix: Path) -> None:
    monkeypatch.setattr(
        build_environment,
        "sys",
        SimpleNamespace(
            prefix=str(prefix), base_prefix="different-base", stderr=sys.stderr
        ),
    )
    monkeypatch.delenv("PYTHONPATH", raising=False)


def test_main_accepts_clean_configuration(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _fake_interpreter(monkeypatch, tmp_path)
    (tmp_path / "pyvenv.cfg").write_text(ISOLATED, encoding="utf-8")
    assert build_environment.main() == 0
    captured = capsys.readouterr()
    assert captured.out == captured.err == ""


def test_main_reports_rejection_without_environment_values(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _fake_interpreter(monkeypatch, tmp_path)
    (tmp_path / "pyvenv.cfg").write_text(
        "include-system-site-packages = true\n", encoding="utf-8"
    )
    monkeypatch.setenv("PYTHONPATH", "private-sentinel-path")
    assert build_environment.main() == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "include-system-site-packages" in captured.err
    assert "PYTHONPATH is set" in captured.err
    assert "private-sentinel-path" not in captured.err


@pytest.mark.parametrize("invalid_encoding", [False, True])
def test_missing_or_unreadable_config_fails_safely(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    invalid_encoding: bool,
) -> None:
    _fake_interpreter(monkeypatch, tmp_path)
    if invalid_encoding:
        (tmp_path / "pyvenv.cfg").write_bytes(b"\xff")
    assert build_environment.main() == 1
    assert "unable to read pyvenv.cfg" in capsys.readouterr().err


def test_nonvenv_interpreter_is_rejected(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        build_environment,
        "sys",
        SimpleNamespace(prefix="same", base_prefix="same", stderr=sys.stderr),
    )
    assert build_environment.main() == 1
    assert "use the project Python 3.14 .venv" in capsys.readouterr().err


def test_isolated_guard_entry_point_rejects_unsafe_environment() -> None:
    script = Path(__file__).resolve().parents[1] / "scripts/build_environment.py"
    process = subprocess.run(
        [sys.executable, "-I", "-S", str(script)],
        env=os.environ | {"PYTHONPATH": "private-sentinel-path"},
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert process.returncode == 1
    expected = (
        "PYTHONPATH is set"
        if sys.prefix != sys.base_prefix
        else "use the project Python 3.14 .venv"
    )
    assert expected in process.stderr
    assert "private-sentinel-path" not in process.stdout + process.stderr
