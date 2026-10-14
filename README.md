# password-strength-checker

[![CI](https://github.com/YOUR_USERNAME/password-strength-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/password-strength-checker/actions/workflows/ci.yml)

A private-by-default Python CLI that estimates password strength, explains weaknesses, and suggests practical improvements.

## Features

- Python 3.14+; zero third-party runtime dependencies.
- Secure no-echo prompt by default; explicit stdin and command-line input options.
- Length and ASCII/Unicode character-class analysis, with estimated entropy and offline crack time.
- Common-password and leetspeak checks against 563 bundled weak-password examples.
- Forward/reverse QWERTY keyboard walks, ascending/descending sequences, repeated characters/blocks, years (1950–2039), valid DDMMYYYY dates, and predictable suffixes.
- Optional personal-context matching without echoing the supplied tokens.
- Scores from 0 (very weak) to 4 (strong), with suggestions ordered by impact.
- Human reports, JSON schema version 1, TTY-aware ANSI colors, and `NO_COLOR` support.
- Opt-in [Have I Been Pwned](https://haveibeenpwned.com/) checks using its password range API.
- Immutable, typed result dataclasses and a deterministic analysis API.

## Installation

Python **3.14 or newer** must be available as `python`. Replace `YOUR_USERNAME` in the clone URL and CI badge with the repository owner. The project is not assumed to be published on PyPI.

From source:

```console
git clone https://github.com/YOUR_USERNAME/password-strength-checker.git
cd password-strength-checker
python -m venv .venv
```

Activate the environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On Linux/macOS, activate with `source .venv/bin/activate` instead. Install and check the command:

```console
python -m pip install .
pwcheck --version
```

Captured version output:

```text
pwcheck 0.1.0
```

For an isolated CLI install with an existing [pipx](https://pipx.pypa.io/) installation, run from the cloned repository:

```console
pipx install --python python .
pwcheck --version
```

Choose a Python 3.14+ executable for `--python` if your default interpreter is older. Both `pwcheck` and `python -m pwcheck` are supported.

## Usage

Run `pwcheck` with no input flags to enter a password securely using `getpass`. The prompt does not echo characters. The program refuses the echoing fallback when a secure terminal is unavailable; use `--stdin` with a trusted source in that situation.

The following five examples and the JSON example contain **public, synthetic demonstration inputs**. Never use them for an account. Outputs were captured from v0.1.0 on Python 3.14. The pipeline examples use PowerShell; after activation, `pwcheck` is on PATH. Writing literal passwords in pipeline commands also exposes them to shell history, so these commands are for demonstration only.

### 1. A familiar password with a digit and punctuation

```powershell
pwcheck --password 'Password1!' --no-color
```

stderr:

```text
Warning: --password exposes the password to shell history and process arguments. Use the secure prompt instead.
```

stdout:

```text
Score: 0/4 (very weak)
Length: 10 characters
Character classes: lowercase, uppercase, digits, symbols
Estimated entropy: 10.0 bits (raw 65.7, penalties 50.0; ceilings may also apply)
Estimated offline crack time: less than 1 second at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - A common password or a predictable variant was found.
  - Trailing digits or symbols form a predictable suffix.
Suggestions (highest impact first):
  - Use a 4-5 word passphrase chosen randomly from a large word list.
  - Replace common passwords entirely; small edits do not help.
  - Do not rely on appending digits or punctuation to a familiar base.
  - Increase length to at least 16 characters.
  - Use a password manager to generate a unique password for each account.
```

Exit code: **1**.

### 2. A keyboard walk through stdin

```powershell
'qwertyuiop' | pwcheck --stdin --no-color
```

```text
Score: 0/4 (very weak)
Length: 10 characters
Character classes: lowercase
Estimated entropy: 0.0 bits (raw 47.0, penalties 60.0; ceilings may also apply)
Estimated offline crack time: less than 1 second at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - A common password or a predictable variant was found.
  - A keyboard walk was found.
Suggestions (highest impact first):
  - Use a 4-5 word passphrase chosen randomly from a large word list.
  - Replace common passwords entirely; small edits do not help.
  - Avoid keyboard walks and choose unrelated words or random characters.
  - Increase length to at least 16 characters.
  - Use a password manager to generate a unique password for each account.
```

Exit code: **1**.

### 3. Personal information disguised with leetspeak

```powershell
'J0hn-Canyon-1998!' | pwcheck --stdin --context 'john,smith,1998,astana' --no-color
```

```text
Score: 1/4 (weak)
Length: 17 characters
Character classes: lowercase, uppercase, digits, symbols
Estimated entropy: 28.0 bits (raw 111.7, penalties 55.0; ceilings may also apply)
Estimated offline crack time: less than 1 second at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - The password contains supplied personal information.
  - A year or calendar date was found.
  - Trailing digits or symbols form a predictable suffix.
Suggestions (highest impact first):
  - Use a 4-5 word passphrase chosen randomly from a large word list.
  - Remove names, birthdays, places, and other personal information.
  - Avoid years and dates, especially birthdays and anniversaries.
  - Do not rely on appending digits or punctuation to a familiar base.
  - Use a password manager to generate a unique password for each account.
```

Exit code: **1**. Findings do not reveal the matched personal token.

### 4. A longer passphrase

```powershell
'orbit velvet canyon lantern' | pwcheck --stdin --no-color
```

```text
Score: 4/4 (strong)
Length: 27 characters
Character classes: lowercase, symbols
Estimated entropy: 158.8 bits (raw 158.8, penalties 0.0; ceilings may also apply)
Estimated offline crack time: over 1 million centuries at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - No listed patterns detected.
Suggestions (highest impact first):
  - Use a password manager to generate a unique password for each account.
```

Exit code: **0**. This output demonstrates the heuristic; it does not establish that these words were chosen randomly. See the passphrase limitation below.

### 5. A 14-character input using the module entry point

```powershell
'mkjvuxpzqswfgh' | python -m pwcheck --stdin --no-color
```

```text
Score: 3/4 (good)
Length: 14 characters
Character classes: lowercase
Estimated entropy: 65.8 bits (raw 65.8, penalties 0.0; ceilings may also apply)
Estimated offline crack time: 1.0 centuries at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - No listed patterns detected.
Suggestions (highest impact first):
  - Increase length to at least 16 characters.
  - Use a password manager to generate a unique password for each account.
```

Exit code: **0**. Length 12–15 is capped at good, even when the entropy estimate is higher.

### JSON example

```powershell
'orbit velvet canyon lantern' | pwcheck --stdin --json
```

```json
{
  "length": 27,
  "character_classes": [
    "lowercase",
    "symbols"
  ],
  "charset_size": 59,
  "raw_entropy_bits": 158.83136233276971,
  "penalty_bits": 0,
  "entropy_bits": 158.83136233276971,
  "score": 4,
  "label": "strong",
  "findings": [],
  "suggestions": [
    "Use a password manager to generate a unique password for each account."
  ],
  "schema_version": 1,
  "offline_guesses_per_second": 10000000000,
  "offline_crack_seconds": 3.250680744240525e+37,
  "offline_crack_time": "over 1 million centuries",
  "hibp": null
}
```

Exit code: **0**. JSON never contains the password, matched substrings, context tokens, or ANSI escape sequences. `hibp` is null unless the optional check was requested. When requested it is an object with `status` (`found`, `not_found`, or `unavailable`), `count` (integer or null), `message`, and `source`. Finding objects contain `kind`, `penalty_bits`, and a fixed public `message`.

All reports include metadata such as length and character classes, so treat the reports as potentially sensitive even though they omit the secret itself.

### Options and exit codes

| Option | Behavior |
| --- | --- |
| No input option | Secure no-echo prompt |
| `--password TEXT` | Explicit input; warns on stderr about shell history and process arguments |
| `--stdin` | Read one password line until EOF; remove one LF/CRLF, preserve spaces |
| `--context TOKENS` | Comma-separated personal tokens, matched case-insensitively after normalization |
| `--json` | JSON schema version 1 on stdout |
| `--hibp` | Opt in to a HIBP range request; disabled by default |
| `--no-color` | Disable ANSI colors |
| `--version` / `--help` | Version / usage information |

Input options are mutually exclusive. The CLI limits passwords to 4096 Unicode code points and rejects multiline stdin. Empty input is analyzed as very weak. The analysis API also handles larger strings, including the 100,000-character cases in the tests.

| Exit code | Meaning |
| --- | --- |
| 0 | Score 3 or 4; also help/version |
| 1 | Score 0, 1, or 2 |
| 2 | Usage, input/output, or requested HIBP check error |

When HIBP is unavailable, local results are still printed, with a generic explanation and exit code 2. A confirmed breach forces score 0 and advice to replace the password everywhere it is used. `NO_COLOR` disables color even when set to an empty value; JSON is always color-free.

## How scoring works

This is an **estimate**, not a measurement of password randomness or a calibrated attack model.

1. Count Unicode code points and observe character classes. Assumed pool sizes are lowercase 26, uppercase 26, ASCII digits 10, ASCII punctuation plus space 33, and other Unicode 100. Observed pools are added together; the Unicode bucket is a conservative heuristic, not the full repertoire.
2. Compute raw bits: `length * log2(charset_size)`; empty input has zero bits.
3. Subtract the following penalties once per detected category, even if categories overlap; clamp the result at zero.

| Finding | Penalty (bits) |
| --- | ---: |
| Common password or suffix-decorated variant | 40 |
| Supplied personal context | 30 |
| Repeated characters or blocks | 25 |
| Keyboard walk | 20 |
| Letter/digit sequence | 15 |
| Year or valid date | 15 |
| Trailing digits/punctuation on a letter-containing base | 10 |

4. Apply entropy ceilings: common passwords at most 10 bits; context matches at most 28 bits; whole-password repetitions at most the repeating unit's raw entropy and 24 bits. A confirmed HIBP breach gives zero bits. `penalty_bits` reports only the additive penalties, so it may differ from `raw_entropy_bits - entropy_bits` after ceilings.
5. Map adjusted bits to scores, then apply length and pattern ceilings.

| Adjusted bits | Base score |
| --- | --- |
| Below 28 | 0 — very weak |
| 28 to below 36 | 1 — weak |
| 36 to below 60 | 2 — fair |
| 60 to below 80 | 3 — good |
| 80 or more | 4 — strong |

| Length | Maximum score |
| --- | --- |
| Below 8 | 0 — very weak |
| 8–11 | 2 — fair |
| 12–15 | 3 — good |
| 16+ | 4 — strong |

Any detected pattern prevents a strong rating. Keyboard walks, sequences, or repetitions cap the score at fair; personal context or whole-password repetition caps it at weak; common passwords and confirmed breaches receive very weak. These are ceilings: sufficient length does not guarantee that score.

Common-password/context comparisons apply Unicode NFKC normalization and case folding, then `@ → a`, `0 → o`, `1 → l/i`, `3 → e`, `$ → s`, `5 → s`, and `7 → t`. Matching collapses i/l to handle ambiguous 1 substitutions without exponential variant expansion; this intentionally permits some false positives. The actual password is neither modified for input nor normalized before HIBP hashing.

The average offline crack-time assumption is `max(1, 2^(entropy_bits - 1)) / 10^10` seconds: roughly half a uniform search space, with a minimum of one guess. Years use 365.25 days. Human output is bounded at “over 1 million centuries”; JSON numeric seconds become null only when the estimate exceeds the supported float range. Hardware, hash algorithms, dictionary attacks, and password reuse can change real crack times dramatically.

Suggestions start with replacing a confirmed breached password, then a randomly chosen 4–5 word passphrase for a low score, then category-specific fixes in descending penalty order, length advice, and a unique-password/password-manager recommendation.

The detector work is O(n) for fixed keyboard/sequence catalogs and bounded block size, plus O(total dictionary/context characters) for comparisons. The prefix-table algorithm for whole-password repetitions takes O(n) time and O(n) temporary space. No password values are cached.

## Security considerations

- The recommended no-echo prompt avoids putting the password in command arguments or shell history. It refuses insecure echo fallback.
- `--password` is available for controlled automation and examples but is discouraged. Other processes may inspect command arguments; the warning goes to stderr so stdout JSON stays valid. `--stdin` keeps passwords out of this program's arguments, but its upstream source must also be trusted.
- The application never logs passwords, saves user passwords to disk, or includes password text or matched context tokens in reports or error messages. It does not retain secret substrings in result dataclasses. Parser errors are generic to avoid argparse's normal argument echo.
- Python strings cannot be reliably erased from memory. This is not a secure-memory or anti-swap tool; the terminal, operating system, shell, or calling process may retain information.
- `--context` itself is a command argument and may expose personal information in shell history or process listings. Only provide context you are comfortable exposing through that channel.
- HIBP is opt-in. The code hashes the exact UTF-8 input using SHA-1 locally and sends **only its first five hexadecimal characters** over HTTPS to `api.pwnedpasswords.com/range/`. The remaining 35-character suffix is compared locally; the password and full hash are never sent. The response requests `Add-Padding: true`, has a 2 MiB read limit, and uses urllib with a 5-second socket timeout. SHA-1 is required by this lookup protocol and is never used here for password storage. See the [official HIBP API documentation](https://haveibeenpwned.com/API/v3#PwnedPasswords).
- K-anonymity reduces disclosure; the service still sees a prefix, your IP address, and request timing. No match does not prove safety. Network/response errors never include raw exceptions or hashes.
- Unit tests mock HIBP and forbid calls to its real HTTP transport. CI does not check real passwords or contact HIBP.

## Limitations

- This is a small, transparent educational heuristic, **not zxcvbn-level analysis**. It does not infer how a password was generated and may overestimate entropy, particularly for meaningful phrases, quotes, familiar word combinations, or undetected dictionary words. A four-word random passphrase's entropy comes from the word-list size and selection process, not this character formula.
- The memory-curated list contains 563 unique lowercase examples, not a statistically ranked “top 563.” It is intentionally small and cannot represent every language, keyboard layout, or leaked-password corpus.
- Keyboard detection is limited to the specified QWERTY rows/vertical path; sequences are ASCII runs of at least four characters. Embedded adjacent repeated blocks are limited to 2–32 characters, with a separate unbounded whole-password repetition detector. Years require digit boundaries; dates are contiguous DDMMYYYY within 1950–2039.
- Short personal tokens, i/l normalization, and conservative pattern ceilings can create false positives. Overlapping findings may subtract more than one penalty for the same characters.
- Length counts code points, not visual grapheme clusters. Other Unicode characters use one approximate bucket, and the CLI does not model an account's encoding or password policies.
- Crack times describe the assumed offline search only. They are not predictions for a particular account, online rate limiting, MFA, or a specific password hash.
- Detection can miss transformations such as prepending predictable text or inserting separators into a weak base. Avoid reuse regardless of the score.

## Project structure

```text
password-strength-checker/
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .github/workflows/ci.yml
├── src/pwcheck/
│   ├── __init__.py          # Version
│   ├── __main__.py          # python -m entry point
│   ├── cli.py               # argparse and input/output orchestration
│   ├── analyzer.py          # Pure scoring and suggestions
│   ├── entropy.py           # Charset, entropy, and crack-time estimates
│   ├── patterns.py          # Pattern detectors and normalization
│   ├── report.py            # Human and JSON formatting
│   ├── hibp.py              # Isolated optional network lookup
│   ├── py.typed
│   └── data/
│       ├── __init__.py
│       └── common_passwords.txt
└── tests/                   # Module tests, CLI tests, and mocked network checks
```

The public dictionary is loaded once through `importlib.resources` when the pattern module is imported. Analysis calls operate only on their inputs and immutable in-memory data; `analyzer.py` performs no file/network I/O or printing. Custom dictionaries and context can be supplied directly for deterministic testing. Reports receive only immutable analysis/breach metadata.

## Development

Use a Python 3.14+ virtual environment and install the two direct development dependencies, pytest and Ruff:

```console
python -m pip install -e ".[dev]"
ruff check .
ruff format .
ruff format --check .
pytest -q
```

The suite covers empty/Unicode/very long input, all detector categories, leetspeak ambiguity, scoring boundaries, secret-free JSON/errors, getpass fallback refusal, CLI exit/color behavior, and mocked HIBP success/failure. GitHub Actions runs the checks on Python 3.14 for pushes and pull requests.

## Roadmap

- Calibrate heuristics against public synthetic fixtures and document false positives.
- Consider dictionary segmentation and a word-generation-aware passphrase estimate.
- Expand keyboard layouts and date formats with regression tests.
- Evaluate a larger, responsibly sourced weak-password corpus.
- Add release automation after publication details are established.

These are planned ideas, not current features.

## License

[MIT](LICENSE), copyright 2026 Your Name. Replace the author placeholder before publishing.
