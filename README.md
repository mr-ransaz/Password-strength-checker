# password-strength-checker

[![CI](https://github.com/mr-ransaz/Password-strength-checker/actions/workflows/ci.yml/badge.svg)](https://github.com/mr-ransaz/Password-strength-checker/actions/workflows/ci.yml)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A private-by-default Python CLI that estimates password strength, explains weaknesses, and suggests practical improvements.

## Features

- Python 3.14 only; zero third-party runtime dependencies.
- Secure no-echo prompt by default; explicit stdin and command-line input options.
- Length and ASCII/Unicode character-class analysis, with estimated entropy and offline crack time.
- Common-password and leetspeak checks against 563 bundled weak-password examples.
- Forward/reverse QWERTY keyboard walks, ascending/descending sequences, repeated characters/blocks, years (1950–2039), valid DDMMYYYY dates, and predictable suffixes.
- Optional personal-context matching without echoing the supplied tokens.
- Scores from 0 (very weak) to 4 (strong), with suggestions ordered by impact.
- Explicit low-score reasons for short inputs, limited character pools, and low estimated entropy, including when no pattern is detected.
- Human reports, JSON schema version 1, TTY-aware ANSI colors, and `NO_COLOR` support.
- Opt-in [Have I Been Pwned](https://haveibeenpwned.com/) checks using its password range API.
- Immutable, typed result dataclasses and a deterministic analysis API.
- Windows console builds: one-file executable, one-folder ZIP, and SHA-256 checksums.
- Frozen no-argument terminal sessions repeat secure prompts until an empty input.

## Installation

Use **Python 3.14.x only** for source installation. Replace `MR_RANSAZ` in package project URLs and download links before publication. Those URLs are placeholders, not verified destinations. The existing CI badge points to this repository, but hosted execution has not been verified. The project is not assumed to be published on PyPI.

Clone your fork using Git. From the project root, use an existing Python 3.14 virtual environment at `.venv`. Creating that environment is a prerequisite to these repository commands; they never invoke global Python.

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip install -e ".[dev]" --no-build-isolation --no-cache-dir
.\.venv\Scripts\python.exe -m pwcheck --version
```

The development install requires setuptools 77+ in the existing environment because build isolation is disabled. This does not add a runtime dependency. For runtime-only installation, omit the `dev` extra. All commands here use the explicit virtualenv interpreter; activation is unnecessary.

Captured version output:

```text
pwcheck 0.2.0
```

An optional isolated installation with [pipx](https://pipx.pypa.io/) can target the local project and an explicit Python 3.14 executable. pipx installation has **not** been verified in this repository session. The installed console script is `pwcheck`; examples below invoke the equivalent module entry point with the explicit interpreter.

## Why this exists / what I learned

This project makes a small password-strength heuristic easy to inspect and test for a cybersecurity portfolio. A character checklist misses familiar passwords and patterns; a score also needs an explanation that reflects its actual length, entropy, and pattern limits.

The implementation records three practical lessons: separate deterministic analysis from secret-handling I/O, treat network lookup failures as explicit outcomes, and distinguish executed evidence from assumptions. The subprocess tests also show why a source checkout needs an explicit import path when testing an uninstalled package. Coverage checks are useful evidence, while live service and CI verification remain separate work.

## Download

The Windows build produces three release assets. These links are **placeholders**;
the v0.2.0 release has not been published or downloaded from GitHub:

- [pwcheck.exe — one file](https://github.com/mr-ransaz/Password-strength-checker/releases/download/v0.2.0/pwcheck.exe)
- [pwcheck-folder.zip — complete one-folder bundle](https://github.com/mr-ransaz/Password-strength-checker/releases/download/v0.2.0/pwcheck-folder.zip)
- [SHA256SUMS.txt — checksums for both assets](https://github.com/mr-ransaz/Password-strength-checker/releases/download/v0.2.0/SHA256SUMS.txt)

Local builds target 64-bit Windows using 64-bit Python 3.14. The bundles include
the interpreter and dictionary; the target machine is intended to need no Python
installation. Running on a separate machine without Python remains **NOT verified**.
For the ZIP, extract the entire folder and keep `pwcheck.exe` beside `_internal`;
do not copy the folder executable out on its own. One-file mode extracts program
libraries/data to a temporary directory at startup; password input is never written
there by pwcheck.

**Verify SHA-256 before running.** Open PowerShell in the directory containing the
downloaded assets and checksum file. For a local build, that directory is `dist`.
This exact verification was also run against the local build:

```powershell
$Entries = Get-Content -LiteralPath .\SHA256SUMS.txt
foreach ($Name in @('pwcheck.exe', 'pwcheck-folder.zip')) {
    $Pattern = '^[a-f0-9]{64}  ' + [regex]::Escape($Name) + '$'
    $Entry = @($Entries | Where-Object { $_ -match $Pattern })
    if ($Entry.Count -ne 1) { throw 'Missing or duplicate checksum.' }
    $Expected = ($Entry[0] -split '  ', 2)[0]
    $Actual = (Get-FileHash -LiteralPath $Name -Algorithm SHA256).Hash
    if ($Actual -ine $Expected) { throw 'SHA-256 mismatch.' }
}
'SHA-256 verified for both assets.'
```

Checksums detect file changes relative to that checksum file; they do not replace
publisher authentication. The executable is **not code-signed**. Windows SmartScreen
or an antivirus **may warn** about it. The user reports no warning on their clean local
v0.2.0 build (PowerShell 7.6.7). Downloaded-asset warning behavior is **NOT VERIFIED**;
that local result does not establish scanner acceptance on other machines.

From the executable's directory, a scripted version check is:

```powershell
.\pwcheck.exe --version
```

Captured local output: `pwcheck 0.2.0` (exit 0). The usual `--stdin`, `--json`,
`--context`, and optional `--hibp` flags use the same CLI logic as source runs.
The smoke script verifies weak/strong stdin inputs and their 1/0 exit codes.

For double-click use, the console-mode executable is designed to prompt through
`getpass`, display a report, and repeat until an empty password. This requires a
frozen executable, no arguments, and terminal stdin/stdout. Empty input ends that
session with exit 0. Any arguments or redirected handles retain single-run CLI
behavior; an empty scripted password still returns 1. Repeat/no-echo control flow
is tested with fakes. The user reports Explorer double-click **PASS** on their clean
local v0.2.0 build; downloaded binaries and other machines remain **NOT VERIFIED**.
The source-module default remains one secure prompt.

## Build the Windows executable locally

Prerequisites: Windows, PowerShell 7.4+, and the existing 64-bit Python 3.14
`.venv`. Run from the project root; global Python is never used:

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev,build]" --no-build-isolation --no-cache-dir
.\scripts\build_exe.ps1
.\scripts\smoke_exe.ps1
```

The `build` extra pins PyInstaller 6.22.3; runtime dependencies remain empty.
Before importing PyInstaller or cleaning outputs, the script runs a stdlib-only
preflight with `-I -S`: `pyvenv.cfg` must explicitly disable system site-packages,
and `PYTHONPATH` must be absent, even if its value would be empty. Unsafe settings
produce fixed diagnostic messages without printing environment values. The build
does not silently clear or repair them; see the recreation steps below.

The script **cleans this repository's `build/` and `dist/` directories**, rejects
linked cleanup targets, and invokes `PyInstaller` through `.venv` Python. Its
documented configuration is `--console --noupx` plus `--onefile` / `--onedir`,
an explicit data mapping for `common_passwords.txt`, and a hidden import of
`pwcheck.data`. Generated specs and caches stay under `build/`. Windows file/product
version resources are generated from `src/pwcheck/__init__.py` and cross-checked
against pyproject metadata. No version resource is hand-edited. A custom icon is
used only when `assets/pwcheck.ico` exists; none was supplied for this build.

Outputs are `dist/pwcheck.exe`, `dist/pwcheck-folder.zip`, and `dist/SHA256SUMS.txt`.
The expanded folder is also left at `dist/folder/pwcheck/`. Artifacts are ignored
by Git. The smoke script validates both checksum entries, Windows version metadata,
and version/weak/strong invocations for all three layouts, including the extracted
ZIP. Each invocation runs from `build/smoke-cwd` with Python-related environment
variables removed and PATH restricted to Windows System32. This passed locally
on this development machine; it is not a substitute for a Python-free machine test.

The tag-triggered [release workflow](.github/workflows/release.yml) defines a
read-only build job and a separate release job with `contents: write`. It requires
the tag to match the package version, runs tests/build/smoke checks, and is configured
to attach all three assets. A rerun may replace those named assets on an existing
release. **The GitHub release workflow has NOT run and is NOT verified.**

## Recreate a clean build environment

The original local v0.2.0 environment inherited global site-packages and an unrelated
project's source directory. The user reports recreating `.venv` with
`include-system-site-packages = false`; their subsequent build search path no longer
contained either source of contamination. Their clean rebuild, checksums, smoke 9/9,
Ruff, format check, and pytest passed. These are **user-reported manual outcomes**.

For a contaminated environment:

1. Deactivate it and close Python/build processes using it.
2. Move the old `.venv` aside as a backup, outside `build/` and `dist/`. Manually
   create a fresh `.venv` using a trusted 64-bit Python 3.14 installation's `venv`
   module with its default isolation; do **not** enable `--system-site-packages`.
   This one-time bootstrap is performed outside the environment being replaced;
   subsequent repository commands use only the new `.venv` interpreter. Do not
   copy the old site-packages or editable-install path files into it.
3. In PowerShell, remove `PYTHONPATH` from the current process, verify the new
   environment, then install the project. This does not change user/system settings.

```powershell
if (Test-Path Env:\PYTHONPATH) { Remove-Item Env:\PYTHONPATH }
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -I -S .\scripts\build_environment.py
.\.venv\Scripts\python.exe -m pip install -e ".[dev,build]"
```

Expected: Python 3.14.x; the preflight exits 0 with no output; installation succeeds.
The follow-up verified these commands against the existing isolated environment,
without recreating it again. If a new shell restores `PYTHONPATH`, correct its source
before building; the guard rejects its presence rather than echoing its value.
Then use the normal build/smoke commands above. Local clean-build success does not
verify GitHub CI, release publication, downloaded assets, or a machine without Python.

## Usage

Run the source CLI with no input flags to enter a password securely using `getpass`. The prompt does not echo characters. The program refuses the echoing fallback when a secure terminal is unavailable; use `--stdin` with a trusted source in that situation. Frozen no-argument terminal sessions use the repeat behavior described above; scripted use is unchanged.

The following six examples and the JSON example contain **public, synthetic demonstration inputs**. Never use them for an account. Outputs are captured from v0.2.0 on Python 3.14. The commands use PowerShell from the project root and the explicit virtualenv interpreter. Writing literal passwords in pipeline commands also exposes them to shell history, so these commands are for demonstration only. Regression tests rerun every usage example and compare stdout, stderr, and exit codes against this README.

### 1. A familiar password with a digit and punctuation

```powershell
.\.venv\Scripts\python.exe -m pwcheck --password 'Password1!' --no-color
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
  - Too short for a good rating: fewer than 12 characters.
  - Low estimated entropy: fewer than 60 bits after penalties and ceilings.
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
'qwertyuiop' | .\.venv\Scripts\python.exe -m pwcheck --stdin --no-color
```

```text
Score: 0/4 (very weak)
Length: 10 characters
Character classes: lowercase
Estimated entropy: 0.0 bits (raw 47.0, penalties 60.0; ceilings may also apply)
Estimated offline crack time: less than 1 second at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - Too short for a good rating: fewer than 12 characters.
  - Single character class: lowercase letters only (smaller estimated search space).
  - Low estimated entropy: fewer than 60 bits after penalties and ceilings.
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
'J0hn-Canyon-1998!' | .\.venv\Scripts\python.exe -m pwcheck --stdin --context 'john,smith,1998,astana' --no-color
```

```text
Score: 1/4 (weak)
Length: 17 characters
Character classes: lowercase, uppercase, digits, symbols
Estimated entropy: 28.0 bits (raw 111.7, penalties 55.0; ceilings may also apply)
Estimated offline crack time: less than 1 second at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - Low estimated entropy: fewer than 60 bits after penalties and ceilings.
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
'orbit velvet canyon lantern' | .\.venv\Scripts\python.exe -m pwcheck --stdin --no-color
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
'mkjvuxpzqswfgh' | .\.venv\Scripts\python.exe -m pwcheck --stdin --no-color
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

### 6. A short digits-only input with no pattern matches

```powershell
'42' | .\.venv\Scripts\python.exe -m pwcheck --stdin --no-color
```

```text
Score: 0/4 (very weak)
Length: 2 characters
Character classes: digits
Estimated entropy: 6.6 bits (raw 6.6, penalties 0.0; ceilings may also apply)
Estimated offline crack time: less than 1 second at 10^10 guesses/second
Estimates are heuristic, not a security guarantee.
Weaknesses:
  - Too short: fewer than 8 characters.
  - Single character class: digits only (smaller estimated search space).
  - Low estimated entropy: fewer than 60 bits after penalties and ceilings.
Suggestions (highest impact first):
  - Use a 4-5 word passphrase chosen randomly from a large word list.
  - Increase length to at least 16 characters.
  - Use a password manager to generate a unique password for each account.
```

Exit code: **1**. A low score still has real explanations when the pattern list is empty.

### JSON example

```powershell
'orbit velvet canyon lantern' | .\.venv\Scripts\python.exe -m pwcheck --stdin --json
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
  "reasons": [],
  "schema_version": 1,
  "offline_guesses_per_second": 10000000000,
  "offline_crack_seconds": 3.250680744240525e+37,
  "offline_crack_time": "over 1 million centuries",
  "hibp": null
}
```

Exit code: **0**. JSON never contains the password, matched substrings, context tokens, or ANSI escape sequences. The additive `reasons` list contains password-free explanations of low scores and is empty when the score is good or strong. `hibp` is null unless the optional check was requested. When requested it is an object with `status` (`found`, `not_found`, or `unavailable`), `count` (integer or null), `message`, and `source`. Finding objects contain `kind`, `penalty_bits`, and a fixed public `message`.

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

For scores below good, reports explain applicable length limits (below 8 or below 12), a single observed character class, and adjusted entropy below 60 bits. These reasons describe the existing calculation and do not add penalties or require mixing character classes. They appear alongside pattern findings in human output and in JSON's `reasons` list.

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
- Live HIBP checks, GitHub-hosted CI, the GitHub release workflow, publication, downloaded-asset checks, pipx, and a machine without Python remain **NOT VERIFIED**. Network unit tests use mocks; checked-in workflows and badges do not establish hosted execution. The user reports local clean-build Explorer double-click PASS with no SmartScreen/antivirus warning; this does not verify downloaded-asset or other-machine behavior. A Kali/Linux VM is not a Windows x64 runtime test.
- Executables are unsigned Windows x64 bundles. No ARM64, 32-bit, or other-machine compatibility is claimed; local smoke checks cover scripted use on this development machine only.

## Project structure

```text
password-strength-checker/
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── AGENTS.md                # Working agreement and gate
├── STATE.md                 # Current checkpoint and open items
├── docs/NOTES.md            # Decisions and verification limits
├── .github/workflows/ci.yml
├── .github/workflows/release.yml
├── scripts/
│   ├── build_exe.ps1         # Clean console-mode bundles and checksums
│   ├── build_environment.py  # Pure isolation checks and preflight entry point
│   ├── smoke_exe.ps1         # Executable/ZIP smoke checks outside project root
│   └── windows_version.py   # Generate version resources from package metadata
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

Use the existing Python 3.14 virtual environment and the three direct development dependencies: pytest, pytest-cov, and Ruff. Runtime dependencies remain empty.

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

The suite covers empty/Unicode/very long input, all detector categories, leetspeak ambiguity, scoring boundaries, secret-free JSON/errors, explicit low-score reasons, getpass fallback refusal, CLI exit/color behavior, install-independent module entry points, README outputs, and mocked HIBP success/failure. pytest configuration automatically measures statements and branches and fails below 90% total coverage, including on the CI workflow's pytest command. No module is excluded to reach the threshold. Subprocess entry points are executed but their coverage is not collected in the parent report.

The workflow defines these checks for Python 3.14 pushes and pull requests; GitHub-hosted execution remains unverified. Follow [AGENTS.md](AGENTS.md), inspect [STATE.md](STATE.md), and record decisions or open checks in [docs/NOTES.md](docs/NOTES.md). STATE must be updated last before the checkpoint commit and local tag.

## Roadmap

- Calibrate heuristics against public synthetic fixtures and document false positives.
- Consider dictionary segmentation and a word-generation-aware passphrase estimate.
- Expand keyboard layouts and date formats with regression tests.
- Evaluate a larger, responsibly sourced weak-password corpus.
- Validate the Windows release workflow and replace publication placeholders.
- Verify downloaded-asset SmartScreen behavior and a Python-free Windows machine before broader support claims.

These are planned ideas, not current features.

## License

[MIT](LICENSE), copyright 2026 Your Name. Replace the author placeholder before publishing.
