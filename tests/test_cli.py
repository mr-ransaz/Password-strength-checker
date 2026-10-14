import getpass
import io
import json
import warnings
from unittest.mock import Mock

import pytest

from pwcheck import cli
from pwcheck.hibp import BreachResult


@pytest.mark.parametrize(
    ("password", "code"),
    [
        ("", 1),
        ("Password1!", 1),
        ("orbit velvet canyon lantern", 0),
        ("mkjvuxpzqswfgh", 0),
    ],
)
def test_password_exit_codes(
    password: str, code: int, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(["--password", password]) == code
    captured = capsys.readouterr()
    assert "shell history" in captured.err
    if password:
        assert password not in captured.out + captured.err


def test_secure_prompt_is_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    prompt = Mock(return_value="orbit velvet canyon lantern")
    monkeypatch.setattr(cli.getpass, "getpass", prompt)
    assert cli.main([]) == 0
    prompt.assert_called_once_with("Password: ")
    assert capsys.readouterr().err == ""


def test_getpass_echoing_fallback_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def insecure(prompt: str) -> str:
        warnings.warn("echo fallback", getpass.GetPassWarning, stacklevel=2)
        raise AssertionError("Should stop before echoing input.")

    monkeypatch.setattr(cli.getpass, "getpass", insecure)
    assert cli.main([]) == 2
    assert "secure input unavailable" in capsys.readouterr().err


@pytest.mark.parametrize(
    "error",
    [
        EOFError(),
        KeyboardInterrupt(),
        OSError("private-secret"),
        UnicodeError("private-secret"),
    ],
)
def test_prompt_errors_are_safe(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    error: BaseException,
) -> None:
    monkeypatch.setattr(cli.getpass, "getpass", Mock(side_effect=error))
    assert cli.main([]) == 2
    captured = capsys.readouterr()
    assert "Error:" in captured.err
    assert "private-secret" not in captured.err
    assert captured.out == ""


@pytest.mark.parametrize(
    ("text", "length"),
    [("abc\n", 3), ("abc\r\n", 3), (" abc \n", 5), ("abc", 3), ("\n", 0), ("", 0)],
)
def test_stdin_line_endings(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    text: str,
    length: int,
) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(text))
    assert cli.main(["--stdin", "--json"]) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["length"] == length
    assert captured.err == ""


@pytest.mark.parametrize("text", ["a\nb\n", "a\rb", "a" * 4097])
def test_stdin_rejects_multiple_lines_and_oversize(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], text: str
) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(text))
    assert cli.main(["--stdin"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert text not in captured.err


def test_cli_length_limit(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("a" * 4096 + "\r\n"))
    assert cli.main(["--stdin", "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["length"] == 4096
    assert cli.main(["--password", "a" * 4097]) == 2
    assert capsys.readouterr().out == ""


def test_cli_context_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    password = "J0hn orbit velvet canyon"
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(password))
    assert (
        cli.main(["--stdin", "--context", " john, smith,1998,astana, ", "--json"]) == 1
    )
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert "personal_context" in {item["kind"] for item in payload["findings"]}
    assert password not in output
    assert "john" not in output.lower()


@pytest.mark.parametrize("json_mode", [False, True])
def test_short_digits_only_cli_report(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    json_mode: bool,
) -> None:
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("42\n"))
    arguments = ["--stdin", "--no-color"]
    if json_mode:
        arguments.append("--json")
    assert cli.main(arguments) == 1
    output = capsys.readouterr().out
    assert "Too short: fewer than 8 characters." in output
    assert "Single character class: digits only" in output
    assert "Low estimated entropy:" in output
    assert "No listed patterns detected." not in output
    if json_mode:
        payload = json.loads(output)
        assert payload["findings"] == []
        assert len(payload["reasons"]) == 3


@pytest.mark.parametrize(
    "args",
    [
        ["--stdin", "--password", "private-secret"],
        ["private-secret"],
        ["--unknown", "private-secret"],
        ["--password"],
        ["--js"],
    ],
)
def test_usage_errors_never_echo_input(
    args: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit) as error:
        cli.main(args)
    assert error.value.code == 2
    captured = capsys.readouterr()
    assert "private-secret" not in captured.err
    assert "usage: pwcheck" in captured.err


@pytest.mark.parametrize(
    ("tty", "no_color", "flag", "json_mode", "colored"),
    [
        (True, False, False, False, True),
        (False, False, False, False, False),
        (True, True, False, False, False),
        (True, False, True, False, False),
        (True, False, False, True, False),
    ],
)
def test_color_policy(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    tty: bool,
    no_color: bool,
    flag: bool,
    json_mode: bool,
    colored: bool,
) -> None:
    if no_color:
        monkeypatch.setenv("NO_COLOR", "")
    else:
        monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.setattr(cli.sys.stdout, "isatty", lambda: tty)
    args = ["--password", "Password1!"]
    if flag:
        args.append("--no-color")
    if json_mode:
        args.append("--json")
    assert cli.main(args) == 1
    assert ("\033[" in capsys.readouterr().out) is colored


def test_hibp_is_off_by_default(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    check = Mock(side_effect=AssertionError("Unexpected network check"))
    monkeypatch.setattr(cli, "check_password", check)
    assert cli.main(["--password", "Password1!"]) == 1
    check.assert_not_called()
    capsys.readouterr()


@pytest.mark.parametrize(
    ("status", "count", "code", "score"),
    [("found", 42, 1, 0), ("not_found", 0, 0, 4), ("unavailable", None, 2, 4)],
)
def test_hibp_cli_status(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    status: str,
    count: int | None,
    code: int,
    score: int,
) -> None:
    password = "orbit velvet canyon lantern"
    monkeypatch.setattr(
        cli,
        "check_password",
        Mock(return_value=BreachResult(status, count, "Test status.")),
    )
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO(password))
    assert cli.main(["--stdin", "--json", "--hibp"]) == code
    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert payload["score"] == score
    assert payload["hibp"]["status"] == status
    assert payload["hibp"]["count"] == count
    assert password not in captured.out + captured.err


def test_output_errors_are_runtime_errors(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(
        cli, "format_human", Mock(side_effect=OSError("private-secret"))
    )
    assert cli.main(["--password", "Password1!"]) == 2
    assert "private-secret" not in capsys.readouterr().err


@pytest.mark.parametrize("flag", ["--version", "--help"])
def test_informational_flags(flag: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as error:
        cli.main([flag])
    assert error.value.code == 0
    captured = capsys.readouterr()
    assert captured.out
    assert captured.err == ""
