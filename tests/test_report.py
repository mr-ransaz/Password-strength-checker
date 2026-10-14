import json

import pytest

from pwcheck.analyzer import analyze_password
from pwcheck.hibp import BreachResult
from pwcheck.report import format_human, format_json


def test_json_schema() -> None:
    password = "orbit velvet canyon lantern"
    output = format_json(analyze_password(password))
    payload = json.loads(output)
    assert set(payload) == {
        "schema_version",
        "length",
        "character_classes",
        "charset_size",
        "raw_entropy_bits",
        "penalty_bits",
        "entropy_bits",
        "score",
        "label",
        "findings",
        "suggestions",
        "reasons",
        "offline_guesses_per_second",
        "offline_crack_seconds",
        "offline_crack_time",
        "hibp",
    }
    assert payload["schema_version"] == 1
    assert isinstance(payload["character_classes"], list)
    assert isinstance(payload["suggestions"], list)
    assert payload["reasons"] == []
    assert payload["hibp"] is None
    assert password not in output
    assert "\033" not in output


def test_finding_json_fields() -> None:
    payload = json.loads(format_json(analyze_password("Password1!")))
    assert set(payload["findings"][0]) == {"kind", "penalty_bits", "message"}
    assert all(
        isinstance(item["penalty_bits"], (int, float)) for item in payload["findings"]
    )


def test_json_overflow_is_null_and_finite() -> None:
    result = analyze_password("山川星空雪月風花雲海森雨光鳥砂石" * 1000 + "橋")
    payload = json.loads(format_json(result))
    assert payload["offline_crack_seconds"] is None
    assert payload["offline_crack_time"] == "over 1 million centuries"


def test_human_findings_and_color() -> None:
    result = analyze_password("Password1!")
    plain = format_human(result)
    assert "Score: 0/4 (very weak)" in plain
    assert "A common password" in plain
    assert "Password1!" not in plain
    assert "\033" not in plain
    assert "\033[31m" in format_human(result, color=True)
    assert "\033[33m" in format_human(analyze_password("mkjvuxpzqs"), color=True)
    assert "\033[32m" in format_human(
        analyze_password("orbit velvet canyon lantern"), color=True
    )


def test_no_patterns_and_empty_classes() -> None:
    output = format_human(analyze_password(""))
    assert "No listed patterns detected." not in output
    assert "Character classes: none" in output
    assert "Too short: fewer than 8 characters." in output
    assert "Low estimated entropy:" in output
    assert "No listed patterns detected." in format_human(
        analyze_password("orbit velvet canyon lantern")
    )


@pytest.mark.parametrize(
    "password", ["", "42", "mkvux", "mkjvuxpzqs", "x6?R", "86720491"]
)
def test_low_scores_without_patterns_have_reasons(password: str) -> None:
    result = analyze_password(password)
    assert result.score < 3
    assert result.findings == ()
    assert result.reasons
    human = format_human(result)
    payload = json.loads(format_json(result))
    assert "No listed patterns detected." not in human
    assert payload["reasons"] == list(result.reasons)
    for reason in result.reasons:
        assert f"  - {reason}" in human


def test_short_digits_only_exact_explanation() -> None:
    result = analyze_password("42")
    expected = [
        "Too short: fewer than 8 characters.",
        "Single character class: digits only (smaller estimated search space).",
        "Low estimated entropy: fewer than 60 bits after penalties and ceilings.",
    ]
    assert json.loads(format_json(result))["reasons"] == expected
    assert "Weaknesses:\n" + "\n".join(
        f"  - {reason}" for reason in expected
    ) in format_human(result)


def test_breach_metadata_in_both_reports() -> None:
    result = analyze_password("orbit velvet canyon lantern", breached=True)
    breach = BreachResult("found", 42, "Found in breached data 42 times; replace it.")
    assert json.loads(format_json(result, breach))["hibp"]["count"] == 42
    assert "Have I Been Pwned" in format_human(result, breach=breach)
