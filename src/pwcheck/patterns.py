"""Bounded, deterministic detectors that never retain matched secret text."""

import re
import string
import unicodedata
from dataclasses import dataclass
from datetime import date
from importlib.resources import files

# Read the public dictionary once at import time, never any user password.
COMMON_PASSWORDS = frozenset(
    files("pwcheck.data")
    .joinpath("common_passwords.txt")
    .read_text(encoding="utf-8")
    .splitlines()
)
_LEET = str.maketrans(
    {"@": "a", "0": "o", "1": "l", "3": "e", "$": "s", "5": "s", "7": "t"}
)
_KEYBOARDS = (
    "qwertyuiop",
    "asdfghjkl",
    "zxcvbnm",
    "1qaz2wsx3edc4rfv5tgb6yhn7ujm8ik9ol0p",
)
_YEAR = re.compile(r"(?<![0-9])(?:19[5-9][0-9]|20[0-3][0-9])(?![0-9])")
_DATE = re.compile(r"(?<![0-9])([0-9]{2})([0-9]{2})([0-9]{4})(?![0-9])")
_SUFFIX = re.compile(r"[0-9!-/:-@\[-`{-~]+$")
_REPEATED_CHAR = re.compile(r"(.)\1{3,}", re.DOTALL)
# Bounded block size avoids unbounded backtracking on very long input.
_REPEATED_BLOCK = re.compile(r"(.{2,32})\1", re.DOTALL)


@dataclass(slots=True, frozen=True)
class Pattern:
    """A weakness with a fixed public description and entropy penalty."""

    kind: str
    penalty_bits: float
    message: str


def normalize_leetspeak(value: str) -> str:
    """Apply NFKC, case folding, and common substitutions (1 becomes l)."""
    return unicodedata.normalize("NFKC", value).casefold().translate(_LEET)


def _match_form(value: str) -> str:
    # Collapse i/l only for comparisons: covers both readings of each '1'
    # without generating exponentially many substitution combinations.
    return normalize_leetspeak(value).replace("l", "i")


def has_keyboard_walk(password: str) -> bool:
    """Detect four-character contiguous walks on rows or vertical QWERTY paths."""
    folded = password.casefold()
    for row in _KEYBOARDS:
        for direction in (row, row[::-1]):
            if any(
                direction[index : index + 4] in folded for index in range(len(row) - 3)
            ):
                return True
    return False


def has_sequence(password: str) -> bool:
    """Detect four or more consecutive ASCII letters or digits in either direction."""
    folded = password.casefold()
    for sequence in (string.ascii_lowercase, string.digits):
        for direction in (sequence, sequence[::-1]):
            if any(
                direction[index : index + 4] in folded
                for index in range(len(sequence) - 3)
            ):
                return True
    return False


def has_repetition(password: str) -> bool:
    """Detect four repeated characters or adjacent blocks of 2-32 characters."""
    return bool(_REPEATED_CHAR.search(password) or _REPEATED_BLOCK.search(password))


def repeating_unit_length(password: str) -> int | None:
    """Find the shortest whole-password repeating unit in O(n) time and space."""
    if not password:
        return None
    prefix = [0] * len(password)
    for index in range(1, len(password)):
        matched = prefix[index - 1]
        while matched and password[index] != password[matched]:
            matched = prefix[matched - 1]
        if password[index] == password[matched]:
            matched += 1
        prefix[index] = matched
    unit = len(password) - prefix[-1]
    return unit if unit < len(password) and len(password) % unit == 0 else None


def has_year_or_date(password: str) -> bool:
    """Detect years 1950-2039 or valid DDMMYYYY dates in that year range."""
    if _YEAR.search(password):
        return True
    for match in _DATE.finditer(password):
        day, month, year = map(int, match.groups())
        if 1950 <= year <= 2039:
            try:
                date(year, month, day)
            except ValueError:
                continue
            return True
    return False


def has_predictable_suffix(password: str) -> bool:
    """Detect trailing ASCII digits/symbols added to a letter-containing base."""
    match = _SUFFIX.search(password)
    return bool(
        match and any(character.isalpha() for character in password[: match.start()])
    )


def is_common_password(
    password: str, common_passwords: frozenset[str] = COMMON_PASSWORDS
) -> bool:
    """Check full and suffix-stripped forms against the curated dictionary."""
    if not password:
        return False
    forms = {_match_form(password)}
    suffix = _SUFFIX.search(password)
    if suffix:
        forms.add(_match_form(password[: suffix.start()]))
    return any(_match_form(candidate) in forms for candidate in common_passwords)


def contains_context(password: str, tokens: tuple[str, ...]) -> bool:
    """Find nonempty personal tokens using case and leetspeak normalization."""
    normalized = _match_form(password)
    return any(
        _match_form(token.strip()) in normalized for token in tokens if token.strip()
    )


def detect_patterns(
    password: str,
    context: tuple[str, ...] = (),
    common_passwords: frozenset[str] = COMMON_PASSWORDS,
) -> tuple[Pattern, ...]:
    """Return at most one safe finding per category in impact order."""
    findings: list[Pattern] = []
    if is_common_password(password, common_passwords):
        findings.append(
            Pattern(
                "common_password",
                40,
                "A common password or a predictable variant was found.",
            )
        )
    if contains_context(password, context):
        findings.append(
            Pattern(
                "personal_context",
                30,
                "The password contains supplied personal information.",
            )
        )
    if has_repetition(password) or repeating_unit_length(password) is not None:
        findings.append(
            Pattern("repetition", 25, "Repeated characters or blocks were found.")
        )
    if has_keyboard_walk(password):
        findings.append(Pattern("keyboard_walk", 20, "A keyboard walk was found."))
    if has_sequence(password):
        findings.append(
            Pattern("sequence", 15, "An ascending or descending sequence was found.")
        )
    if has_year_or_date(password):
        findings.append(
            Pattern("year_or_date", 15, "A year or calendar date was found.")
        )
    if has_predictable_suffix(password):
        findings.append(
            Pattern(
                "predictable_suffix",
                10,
                "Trailing digits or symbols form a predictable suffix.",
            )
        )
    return tuple(findings)
