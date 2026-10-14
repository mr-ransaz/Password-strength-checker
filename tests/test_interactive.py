import io
from unittest.mock import Mock

import pytest

from pwcheck import cli


def _freeze_with_terminals(
    monkeypatch: pytest.MonkeyPatch, *, stdin_tty: bool = True, stdout_tty: bool = True
) -> None:
    monkeypatch.setattr(cli.sys, "frozen", True, raising=False)
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: stdin_tty)
    monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: stdout_tty)
    monkeypatch.setenv("NO_COLOR", "")


def test_frozen_terminal_repeats_secure_prompt_until_empty(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _freeze_with_terminals(monkeypatch)
    prompt = Mock(side_effect=["Password1!", "orbit velvet canyon lantern", ""])
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    monkeypatch.setattr(
        cli, "check_password", Mock(side_effect=AssertionError("Network"))
    )
    assert cli.main([]) == 0
    assert prompt.call_count == 3
    assert all(call.args == ("Password: ",) for call in prompt.call_args_list)
    captured = capsys.readouterr()
    assert "enter an empty password to exit" in captured.out
    assert "Score: 0/4 (very weak)" in captured.out
    assert "Score: 4/4 (strong)" in captured.out
    assert captured.out.count("Score:") == 2
    assert "Password1!" not in captured.out + captured.err
    assert "orbit velvet canyon lantern" not in captured.out + captured.err
    assert captured.err == ""


def test_empty_first_prompt_exits_without_a_report(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _freeze_with_terminals(monkeypatch)
    monkeypatch.setattr(cli.getpass, "getpass", Mock(return_value=""))
    assert cli.main([]) == 0
    assert "Score:" not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("stdin_tty", "stdout_tty"), [(False, True), (True, False), (False, False)]
)
def test_redirected_frozen_run_remains_single_shot(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    stdin_tty: bool,
    stdout_tty: bool,
) -> None:
    _freeze_with_terminals(monkeypatch, stdin_tty=stdin_tty, stdout_tty=stdout_tty)
    prompt = Mock(return_value="")
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    assert cli.main([]) == 1
    prompt.assert_called_once_with("Password: ")
    captured = capsys.readouterr()
    assert "enter an empty password to exit" not in captured.out
    assert captured.out.count("Score:") == 1


def test_nonfrozen_terminal_run_is_unchanged(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _freeze_with_terminals(monkeypatch)
    monkeypatch.setattr(cli.sys, "frozen", False)
    prompt = Mock(return_value="Password1!")
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    assert cli.main([]) == 1
    prompt.assert_called_once()
    assert "enter an empty password to exit" not in capsys.readouterr().out


@pytest.mark.parametrize("argv", [["--no-color"], ["--json"]])
def test_explicit_options_disable_the_loop(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
) -> None:
    _freeze_with_terminals(monkeypatch)
    prompt = Mock(return_value="Password1!")
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    assert cli.main(argv) == 1
    prompt.assert_called_once()
    assert "enter an empty password to exit" not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("text", "code"),
    [("Password1!\n", 1), ("orbit velvet canyon lantern\n", 0), ("\n", 1)],
)
def test_frozen_stdin_exit_codes(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    text: str,
    code: int,
) -> None:
    _freeze_with_terminals(monkeypatch)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(text))
    prompt = Mock(side_effect=AssertionError("Unexpected prompt"))
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    assert cli.main(["--stdin"]) == code
    prompt.assert_not_called()
    assert "enter an empty password to exit" not in capsys.readouterr().out


@pytest.mark.parametrize(
    "error", [EOFError(), KeyboardInterrupt(), OSError("private-secret")]
)
def test_interactive_input_errors_are_safe(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: BaseException,
) -> None:
    _freeze_with_terminals(monkeypatch)
    monkeypatch.setattr(cli.getpass, "getpass", Mock(side_effect=error))
    assert cli.main([]) == 2
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "private-secret" not in captured.out + captured.err


def test_default_argv_uses_process_arguments(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _freeze_with_terminals(monkeypatch)
    monkeypatch.setattr(cli.sys, "argv", ["pwcheck.exe"])
    monkeypatch.setattr(cli.getpass, "getpass", Mock(return_value=""))
    assert cli.main() == 0
    assert "Score:" not in capsys.readouterr().out
