from dataclasses import FrozenInstanceError, asdict

import pytest

from pwcheck.analyzer import LABELS, analyze_password, score_from_entropy


def test_empty_password() -> None:
    result = analyze_password("")
    assert (result.score, result.entropy_bits, result.length) == (0, 0, 0)
    assert result.label == "very weak"
    assert result.character_classes == ()
    assert result.suggestions
    assert "Too short: fewer than 8 characters." in result.reasons


@pytest.mark.parametrize(
    ("bits", "expected"),
    [
        (0, 0),
        (27.99, 0),
        (28, 1),
        (35.99, 1),
        (36, 2),
        (59.99, 2),
        (60, 3),
        (79.99, 3),
        (80, 4),
    ],
)
def test_entropy_score_boundaries(bits: float, expected: int) -> None:
    assert score_from_entropy(bits, 20) == expected


@pytest.mark.parametrize(
    ("length", "expected"), [(0, 0), (7, 0), (8, 2), (11, 2), (12, 3), (15, 3), (16, 4)]
)
def test_length_score_boundaries(length: int, expected: int) -> None:
    assert score_from_entropy(100, length) == expected


@pytest.mark.parametrize("password", ["Password1!", "P@ssw0rd123!", "qwerty", "123456"])
def test_common_passwords_stay_very_weak(password: str) -> None:
    result = analyze_password(password)
    assert result.score == 0
    assert result.entropy_bits <= 10
    assert "common_password" in {finding.kind for finding in result.findings}


def test_unicode_and_passphrase() -> None:
    result = analyze_password("orbit velvet canyon lantern")
    assert result.score == 4
    assert result.label == LABELS[4]
    assert result.findings == ()
    assert result.reasons == ()
    assert analyze_password("山川星空雪月風花雲海森雨光鳥砂石").score == 4


def test_long_input_repetition_is_weak() -> None:
    result = analyze_password("ab" * 50_000)
    assert result.length == 100_000
    assert result.score <= 1
    assert result.entropy_bits <= 24
    assert len(result.findings) <= 7


def test_personal_context_caps_and_privacy() -> None:
    password = "J0hn orbit velvet canyon"
    result = analyze_password(password, ("john",))
    assert result.score <= 1
    assert result.entropy_bits <= 28
    assert password not in str(asdict(result))
    assert "john" not in str(asdict(result)).lower()


@pytest.mark.parametrize(
    ("password", "description"),
    [
        ("mkvux", "lowercase letters only"),
        ("MKVUX", "uppercase letters only"),
        ("42", "digits only"),
        ("!?", "symbols only"),
        ("山川", "other Unicode characters only"),
    ],
)
def test_single_class_low_score_reasons(password: str, description: str) -> None:
    result = analyze_password(password)
    assert result.score < 3
    assert any(description in reason for reason in result.reasons)


def test_reasons_explain_length_cap_without_low_entropy() -> None:
    result = analyze_password("mK8?vR2!xZg")
    assert result.findings == ()
    assert result.entropy_bits >= 60
    assert result.score == 2
    assert result.reasons == ("Too short for a good rating: fewer than 12 characters.",)


def test_pattern_score_caps() -> None:
    result = analyze_password("qwerty violet canyon lantern")
    assert result.score <= 2
    assert result.entropy_bits < result.raw_entropy_bits
    assert analyze_password("orbit velvet canyon 1998").score <= 3


def test_compromised_password_override() -> None:
    result = analyze_password("orbit velvet canyon lantern", breached=True)
    assert result.score == 0
    assert result.entropy_bits == 0
    assert "breached" in result.suggestions[0]


def test_determinism_immutability_and_custom_dictionary() -> None:
    assert analyze_password("example") == analyze_password("example")
    result = analyze_password("rare-base", common_passwords=frozenset({"rare-base"}))
    assert result.score == 0
    with pytest.raises(FrozenInstanceError):
        result.score = 4  # type: ignore[misc]


def test_suggestions_order_and_deduplication() -> None:
    result = analyze_password("Password1998!", ("1998",))
    assert "4-5 word" in result.suggestions[0]
    assert "common passwords" in result.suggestions[1]
    assert "personal information" in result.suggestions[2]
    assert len(result.suggestions) == len(set(result.suggestions))
