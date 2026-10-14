import math

import pytest

from pwcheck.entropy import (
    analyze_charset,
    crack_seconds,
    estimate_entropy,
    format_crack_time,
)


@pytest.mark.parametrize(
    ("password", "classes", "size"),
    [
        ("", (), 0),
        ("abc", ("lowercase",), 26),
        ("ABC", ("uppercase",), 26),
        ("012", ("digits",), 10),
        ("! ", ("symbols",), 33),
        ("é你好١", ("other_unicode",), 100),
        (
            "aA1!é",
            ("lowercase", "uppercase", "digits", "symbols", "other_unicode"),
            195,
        ),
    ],
)
def test_charset(password: str, classes: tuple[str, ...], size: int) -> None:
    result = analyze_charset(password)
    assert result.classes == classes
    assert result.charset_size == size


def test_entropy_formula_and_penalties() -> None:
    assert estimate_entropy(10, 26) == pytest.approx(10 * math.log2(26))
    assert estimate_entropy(10, 26, 12) == pytest.approx(10 * math.log2(26) - 12)
    assert estimate_entropy(1, 2, 100) == 0
    assert estimate_entropy(0, 26) == 0
    assert estimate_entropy(12, 0) == 0


@pytest.mark.parametrize(
    ("length", "charset", "penalty"),
    [(-1, 26, 0), (10, -1, 0), (10, 26, -1), (10, 26, math.nan), (10, 26, math.inf)],
)
def test_invalid_entropy(length: int, charset: int, penalty: float) -> None:
    with pytest.raises(ValueError):
        estimate_entropy(length, charset, penalty)


def test_average_crack_time() -> None:
    assert crack_seconds(0) == pytest.approx(1e-10)
    assert crack_seconds(40) == pytest.approx(2**39 / 10**10)
    assert crack_seconds(1_000_000) is None
    assert format_crack_time(1_000_000) == "over 1 million centuries"


@pytest.mark.parametrize("bits", [-1, math.inf, math.nan])
def test_invalid_crack_entropy(bits: float) -> None:
    with pytest.raises(ValueError):
        crack_seconds(bits)


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0.01, "less than 1 second"),
        (2, "2.0 seconds"),
        (120, "2.0 minutes"),
        (7200, "2.0 hours"),
        (172800, "2.0 days"),
        (2 * 365.25 * 86400, "2.0 years"),
        (200 * 365.25 * 86400, "2.0 centuries"),
    ],
)
def test_time_units(seconds: float, expected: str) -> None:
    assert format_crack_time(math.log2(seconds * 10**10) + 1) == expected
