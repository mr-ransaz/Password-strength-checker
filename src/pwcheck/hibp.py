"""Opt-in Have I Been Pwned range checks; no password or full hash is sent."""

import hashlib
import re
from dataclasses import dataclass
from urllib.error import URLError
from urllib.request import Request, urlopen

from pwcheck import __version__

TIMEOUT_SECONDS = 5
MAX_RESPONSE_BYTES = 2 * 1024 * 1024
_RECORD = re.compile(r"([0-9A-Fa-f]{35}):([0-9]{1,15})")


@dataclass(slots=True, frozen=True)
class BreachResult:
    """A password-free result; count is unknown when the service is unavailable."""

    status: str
    count: int | None
    message: str
    source: str = "https://haveibeenpwned.com/"


def check_password(password: str) -> BreachResult:
    """Query the five-character SHA-1 prefix with TLS, padding, and a 5s timeout.

    SHA-1 is used only because the range protocol requires it, never for
    password storage. Response records are checked locally against the suffix.
    Network, malformed-response, and encoding failures return a generic status.
    """
    try:
        digest = (
            hashlib.sha1(password.encode("utf-8"), usedforsecurity=False)
            .hexdigest()
            .upper()
        )
        request = Request(
            f"https://api.pwnedpasswords.com/range/{digest[:5]}",
            headers={"User-Agent": f"pwcheck/{__version__}", "Add-Padding": "true"},
        )
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if not body or len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("Invalid range response size.")
        count = 0
        for line in body.decode("ascii").splitlines():
            record = _RECORD.fullmatch(line)
            if record is None:
                raise ValueError("Invalid range response record.")
            suffix, occurrences = record.groups()
            if suffix.upper() == digest[5:]:
                count = max(count, int(occurrences))
        if count:
            return BreachResult(
                "found", count, f"Found in breached data {count:,} times; replace it."
            )
        return BreachResult(
            "not_found",
            0,
            "No match in the returned range; this does not prove safety.",
        )
    except OSError, URLError, UnicodeError, ValueError:
        return BreachResult(
            "unavailable",
            None,
            "Check unavailable (network or response error); local analysis only.",
        )
