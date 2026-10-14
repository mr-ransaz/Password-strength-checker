import pytest

from pwcheck.patterns import (
    COMMON_PASSWORDS,
    contains_context,
    detect_patterns,
    has_keyboard_walk,
    has_predictable_suffix,
    has_repetition,
    has_sequence,
    has_year_or_date,
    is_common_password,
    normalize_leetspeak,
    repeating_unit_length,
)


def test_dictionary_is_packaged_unique_and_lowercase() -> None:
    assert 450 <= len(COMMON_PASSWORDS) <= 600
    assert all(word and word == word.lower() for word in COMMON_PASSWORDS)
    assert {"password", "123456", "qwerty"} <= COMMON_PASSWORDS


@pytest.mark.parametrize(
    "password",
    [
        "qwerty",
        "YTREWQ",
        "asdf",
        "fdsa",
        "zxcvbn",
        "nbvcxz",
        "1qaz2wsx",
        "xsw2zaq1",
        "prefix-qwer-tail",
    ],
)
def test_keyboard_walks(password: str) -> None:
    assert has_keyboard_walk(password)


@pytest.mark.parametrize("password", ["", "qwe", "orbit velvet", "1q2w"])
def test_keyboard_negatives(password: str) -> None:
    assert not has_keyboard_walk(password)


@pytest.mark.parametrize(
    "password", ["abcd", "ABCD", "dcba", "1234", "9876", "prefix-4567-tail"]
)
def test_sequences(password: str) -> None:
    assert has_sequence(password)


@pytest.mark.parametrize("password", ["", "abc", "123", "012", "8901", "13579", "aBcE"])
def test_sequence_negatives(password: str) -> None:
    assert not has_sequence(password)


@pytest.mark.parametrize(
    "password", ["aaaa", "abcabc", "abab", "你好你好", "\n\n\n\n", "prefix-xyzxyz-tail"]
)
def test_repetitions(password: str) -> None:
    assert has_repetition(password)


@pytest.mark.parametrize("password", ["", "aaa", "abcabd", "orbit velvet"])
def test_repetition_negatives(password: str) -> None:
    assert not has_repetition(password)


@pytest.mark.parametrize(
    ("password", "unit"),
    [
        ("", None),
        ("abc", None),
        ("abcabc", 3),
        ("aaaa", 1),
        ("aabcaabc", 4),
        ("abcdabc", None),
    ],
)
def test_repeating_unit(password: str, unit: int | None) -> None:
    assert repeating_unit_length(password) == unit


def test_large_repeating_block() -> None:
    block = "a" * 40 + "b"
    assert repeating_unit_length(block * 2000) == len(block)


@pytest.mark.parametrize(
    "password", ["1950", "2039", "name1998!", "01011998", "29022000", "31122039"]
)
def test_years_and_dates(password: str) -> None:
    assert has_year_or_date(password)


@pytest.mark.parametrize(
    "password",
    ["1949", "2040", "29022001", "31022000", "00001998", "01012040", "11998000"],
)
def test_date_negatives(password: str) -> None:
    assert not has_year_or_date(password)


@pytest.mark.parametrize(
    "password", ["Password1!", "mystery123", "orbit!!", "n0vel7!", "名字12!"]
)
def test_suffixes(password: str) -> None:
    assert has_predictable_suffix(password)


@pytest.mark.parametrize(
    "password", ["", "123456", "!@#$", "12!mystery", "orbit", "orbit 123"]
)
def test_suffix_negatives(password: str) -> None:
    # Spaces in a base are valid: the suffix is still predictable.
    if password == "orbit 123":
        assert has_predictable_suffix(password)
    else:
        assert not has_predictable_suffix(password)


@pytest.mark.parametrize(
    "password",
    [
        "password",
        "PASSWORD",
        "P@ssw0rd",
        "Pa$$w0rd1!",
        "Password1!",
        "adm1n",
        "１ｌｏｖｅｙｏｕ",
        "1l1l",
    ],
)
def test_common_normalization(password: str) -> None:
    assert is_common_password(password, COMMON_PASSWORDS | {"ilil"})


def test_normalization_mapping() -> None:
    assert normalize_leetspeak("@013$57") == "aolesst"
    assert normalize_leetspeak("ＰＡＳＳＷＯＲＤ") == "password"
    assert not is_common_password("", COMMON_PASSWORDS)
    assert not is_common_password("orbit velvet canyon lantern")


@pytest.mark.parametrize(
    ("password", "tokens", "found"),
    [
        ("J0hn-Novel", ("john",), True),
        ("Sm1th-Novel", ("smith",), True),
        ("1998-new", ("1998",), True),
        ("astana-river", (" ASTANA ",), True),
        ("strasse-river", ("straße",), True),
        ("lili", ("1i1i",), True),
        ("orbit velvet", ("", " "), False),
        ("orbit velvet", ("john",), False),
    ],
)
def test_context(password: str, tokens: tuple[str, ...], found: bool) -> None:
    assert contains_context(password, tokens) is found


def test_findings_are_safe_and_unique() -> None:
    password = "john-password-qwerty-abcabc1998!"
    findings = detect_patterns(password, ("john",))
    kinds = [finding.kind for finding in findings]
    assert kinds[0] == "personal_context"
    assert len(kinds) == len(set(kinds))
    assert all(
        password not in finding.message and "john" not in finding.message
        for finding in findings
    )


def test_long_symbols_with_no_suffix() -> None:
    password = "!" * 100_000 + "a"
    assert not has_predictable_suffix(password)
    assert not is_common_password(password)
