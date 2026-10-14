"""Pure, deterministic scoring and suggestions; no I/O or network access."""

from dataclasses import dataclass

from pwcheck.entropy import analyze_charset, estimate_entropy
from pwcheck.patterns import (
    COMMON_PASSWORDS,
    Pattern,
    detect_patterns,
    repeating_unit_length,
)

LABELS = ("very weak", "weak", "fair", "good", "strong")
_SUGGESTIONS = {
    "common_password": "Replace common passwords entirely; small edits do not help.",
    "personal_context": (
        "Remove names, birthdays, places, and other personal information."
    ),
    "repetition": "Avoid repeated characters or repeated blocks.",
    "keyboard_walk": (
        "Avoid keyboard walks and choose unrelated words or random characters."
    ),
    "sequence": "Avoid ascending or descending letter and number sequences.",
    "year_or_date": "Avoid years and dates, especially birthdays and anniversaries.",
    "predictable_suffix": (
        "Do not rely on appending digits or punctuation to a familiar base."
    ),
}


@dataclass(slots=True, frozen=True)
class AnalysisResult:
    """Password-free analysis metadata, estimates, and ordered guidance."""

    length: int
    character_classes: tuple[str, ...]
    charset_size: int
    raw_entropy_bits: float
    penalty_bits: float
    entropy_bits: float
    score: int
    label: str
    findings: tuple[Pattern, ...]
    suggestions: tuple[str, ...]


def score_from_entropy(entropy_bits: float, length: int) -> int:
    """Map estimated bits to 0-4 and enforce the documented length ceilings."""
    if entropy_bits < 28:
        score = 0
    elif entropy_bits < 36:
        score = 1
    elif entropy_bits < 60:
        score = 2
    elif entropy_bits < 80:
        score = 3
    else:
        score = 4
    if length < 8:
        return 0
    if length < 12:
        return min(score, 2)
    if length < 16:
        return min(score, 3)
    return score


def analyze_password(
    password: str,
    context: tuple[str, ...] = (),
    common_passwords: frozenset[str] = COMMON_PASSWORDS,
    *,
    breached: bool = False,
) -> AnalysisResult:
    """Estimate strength without retaining the password or context tokens.

    Penalties are per detected category, even when patterns overlap. Entropy
    ceilings prevent trivial constructions from benefiting from extra length.
    Score ceilings reflect weaknesses that the charset formula cannot model.
    A confirmed breach always receives zero bits and a very weak score.
    """
    charset = analyze_charset(password)
    findings = detect_patterns(password, context, common_passwords)
    raw_bits = estimate_entropy(len(password), charset.charset_size)
    penalty = sum(finding.penalty_bits for finding in findings)
    bits = estimate_entropy(len(password), charset.charset_size, penalty)
    kinds = {finding.kind for finding in findings}
    unit_length = repeating_unit_length(password)
    if unit_length is not None:
        bits = min(bits, estimate_entropy(unit_length, charset.charset_size), 24.0)
    if "common_password" in kinds:
        bits = min(bits, 10.0)
    if "personal_context" in kinds:
        bits = min(bits, 28.0)
    if breached:
        bits = 0.0
    score = score_from_entropy(bits, len(password))
    if findings:
        score = min(score, 3)
    if kinds & {"keyboard_walk", "sequence", "repetition"}:
        score = min(score, 2)
    if "personal_context" in kinds or unit_length is not None:
        score = min(score, 1)
    if "common_password" in kinds or breached:
        score = 0
    suggestions: list[str] = []
    if breached:
        suggestions.append("Replace this breached password everywhere it is used.")
    if score < 3:
        suggestions.append(
            "Use a 4-5 word passphrase chosen randomly from a large word list."
        )
    suggestions.extend(_SUGGESTIONS[finding.kind] for finding in findings)
    if len(password) < 16:
        suggestions.append("Increase length to at least 16 characters.")
    suggestions.append(
        "Use a password manager to generate a unique password for each account."
    )
    return AnalysisResult(
        length=len(password),
        character_classes=charset.classes,
        charset_size=charset.charset_size,
        raw_entropy_bits=raw_bits,
        penalty_bits=penalty,
        entropy_bits=bits,
        score=score,
        label=LABELS[score],
        findings=findings,
        suggestions=tuple(suggestions),
    )
