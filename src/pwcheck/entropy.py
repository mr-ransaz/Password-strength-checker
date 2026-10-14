"""Charset-based entropy estimates, not measured password randomness."""

import math
import string
from dataclasses import dataclass

GUESSES_PER_SECOND = 10_000_000_000
_CLASS_SIZES = {
    "lowercase": 26,
    "uppercase": 26,
    "digits": 10,
    "symbols": 33,
    "other_unicode": 100,
}


@dataclass(slots=True, frozen=True)
class CharsetAnalysis:
    """Observed character classes and their assumed search-space size."""

    classes: tuple[str, ...]
    charset_size: int


def analyze_charset(password: str) -> CharsetAnalysis:
    """Classify ASCII characters and use a conservative Unicode bucket.

    The 100-character Unicode bucket is an assumption, not the full Unicode
    repertoire. Non-ASCII letters and digits all belong to this bucket.
    """
    present: set[str] = set()
    for character in password:
        if character in string.ascii_lowercase:
            present.add("lowercase")
        elif character in string.ascii_uppercase:
            present.add("uppercase")
        elif character in string.digits:
            present.add("digits")
        elif character in string.punctuation or character == " ":
            present.add("symbols")
        else:
            present.add("other_unicode")
    classes = tuple(name for name in _CLASS_SIZES if name in present)
    return CharsetAnalysis(classes, sum(_CLASS_SIZES[name] for name in classes))


def estimate_entropy(length: int, charset_size: int, penalty_bits: float = 0) -> float:
    """Estimate bits as length * log2(charset_size) minus heuristic penalties.

    Negative inputs are invalid; an empty search space has zero entropy.
    This estimate assumes independent random characters before penalties.
    """
    if (
        length < 0
        or charset_size < 0
        or not math.isfinite(penalty_bits)
        or penalty_bits < 0
    ):
        raise ValueError("Entropy inputs must be finite and nonnegative.")
    if length == 0 or charset_size == 0:
        return 0.0
    return max(0.0, length * math.log2(charset_size) - penalty_bits)


def crack_seconds(entropy_bits: float) -> float | None:
    """Estimate average offline time at 10^10 guesses/s; None means overflow.

    A uniform space takes about half its size to search on average, with at
    least one guess. This does not model a particular password hashing scheme.
    """
    if not math.isfinite(entropy_bits) or entropy_bits < 0:
        raise ValueError("Entropy must be finite and nonnegative.")
    exponent = max(0.0, entropy_bits - 1) - math.log2(GUESSES_PER_SECOND)
    if exponent > 1023:
        return None
    return 2.0**exponent


def format_crack_time(entropy_bits: float) -> str:
    """Render estimated offline time in bounded human-readable units."""
    seconds = crack_seconds(entropy_bits)
    century = 100 * 365.25 * 24 * 60 * 60
    if seconds is None or seconds >= 1_000_000 * century:
        return "over 1 million centuries"
    if seconds < 1:
        return "less than 1 second"
    units = (
        (century, "centuries"),
        (century / 100, "years"),
        (86400, "days"),
        (3600, "hours"),
        (60, "minutes"),
        (1, "seconds"),
    )
    for divisor, unit in units:
        if seconds >= divisor:
            return f"{seconds / divisor:.1f} {unit}"
    raise AssertionError("Unreachable time unit.")
