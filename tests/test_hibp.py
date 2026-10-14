import hashlib
import io
from unittest.mock import Mock
from urllib.error import HTTPError, URLError

import pytest

from pwcheck import __version__, hibp

PASSWORD = "public-test-example"
DIGEST = hashlib.sha1(PASSWORD.encode(), usedforsecurity=False).hexdigest().upper()


def mock_response(monkeypatch: pytest.MonkeyPatch, body: bytes) -> Mock:
    mock = Mock(return_value=io.BytesIO(body))
    monkeypatch.setattr(hibp, "urlopen", mock)
    return mock


def test_found_and_request_privacy(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = mock_response(monkeypatch, f"{'0' * 35}:0\r\n{DIGEST[5:]}:1234\r\n".encode())
    result = hibp.check_password(PASSWORD)
    assert (result.status, result.count) == ("found", 1234)
    request = mock.call_args.args[0]
    assert request.full_url == f"https://api.pwnedpasswords.com/range/{DIGEST[:5]}"
    assert request.data is None
    assert request.get_header("Add-padding") == "true"
    assert request.get_header("User-agent") == f"pwcheck/{__version__}"
    assert mock.call_args.kwargs == {"timeout": 5}
    assert PASSWORD not in repr(request.__dict__)
    assert DIGEST not in repr(request.__dict__)
    assert DIGEST[5:] not in repr(request.__dict__)


def test_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_response(monkeypatch, f"{'0' * 35}:12\r\n".encode())
    result = hibp.check_password(PASSWORD)
    assert (result.status, result.count) == ("not_found", 0)
    assert "does not prove safety" in result.message


def test_zero_count_padding_and_lowercase(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_response(monkeypatch, f"{DIGEST[5:].lower()}:0\n".encode())
    assert hibp.check_password(PASSWORD).status == "not_found"
    mock_response(monkeypatch, f"{DIGEST[5:].lower()}:9\n".encode())
    assert hibp.check_password(PASSWORD).count == 9


@pytest.mark.parametrize(
    "error",
    [
        URLError("offline"),
        TimeoutError("timeout"),
        HTTPError("https://example.test", 429, "rate limited", {}, None),
    ],
)
def test_network_errors(monkeypatch: pytest.MonkeyPatch, error: Exception) -> None:
    monkeypatch.setattr(hibp, "urlopen", Mock(side_effect=error))
    result = hibp.check_password(PASSWORD)
    assert (result.status, result.count) == ("unavailable", None)
    assert PASSWORD not in result.message


@pytest.mark.parametrize(
    "body",
    [
        b"",
        b"garbage",
        b"A:1",
        b"\xff",
        b"A" * 35 + b":-1",
        b"A" * (hibp.MAX_RESPONSE_BYTES + 1),
    ],
    ids=["empty", "garbage", "short-hash", "non-ascii", "negative-count", "oversize"],
)
def test_invalid_response(monkeypatch: pytest.MonkeyPatch, body: bytes) -> None:
    mock_response(monkeypatch, body)
    assert hibp.check_password(PASSWORD).status == "unavailable"


def test_invalid_unicode_is_safe(monkeypatch: pytest.MonkeyPatch) -> None:
    mock = Mock()
    monkeypatch.setattr(hibp, "urlopen", mock)
    assert hibp.check_password("\ud800").status == "unavailable"
    mock.assert_not_called()


def test_duplicate_records_use_maximum(monkeypatch: pytest.MonkeyPatch) -> None:
    mock_response(monkeypatch, f"{DIGEST[5:]}:9\n{DIGEST[5:]}:4\n".encode())
    assert hibp.check_password(PASSWORD).count == 9
