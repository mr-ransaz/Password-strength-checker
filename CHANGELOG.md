# Changelog

## [Unreleased]

### Fixed

- Refuse Windows builds before cleanup/PyInstaller when system site-packages are
  enabled or PYTHONPATH is present, including empty values. The preflight runs
  with isolated/no-site startup and returns fixed diagnostics without path values.
- Add pure-check and preflight regression tests, and document clean-venv recreation.

### Verification notes

- User reports clean-venv rebuild/checksums, smoke 9/9, lint/format/tests, and local
  Explorer double-click PASS on PowerShell 7.6.7, with no SmartScreen/antivirus warning.
- Downloaded assets, GitHub CI/release workflow, publication, and a Python-free
  Windows machine remain NOT VERIFIED. The v0.2.0 tag is not moved.

## [0.2.0] - 2026-10-15

### Added

- Optional `build` extra pinning PyInstaller 6.22.3 with verified Python 3.14 support.
- Frozen no-argument terminal mode: secure getpass/report loop until empty input;
  source and scripted exit-code behavior remains unchanged.
- Windows build/smoke scripts for a console-mode one-file executable and one-folder
  ZIP, explicit bundled dictionary, no UPX, generated version resources, and SHA-256.
- Fake-based interactive regression tests and version-resource generator tests.
- A tag-triggered Windows release workflow with read-only builds and write access
  limited to the release job; hosted execution remains unverified.
- Download placeholders, checksum instructions, local build guidance, and unsigned
  executable/SmartScreen and manual-verification notes.

### Verified locally

- Python 3.14 Windows builds and nine smoke invocations across the executable,
  expanded folder, and extracted ZIP, with alternate working directory and restricted
  Python environment; version metadata, dictionary loading, and checksums pass.
- At the original checkpoint, Explorer/SmartScreen results were unverified; see
  the later user-reported local results above. Python-free-machine execution,
  downloaded assets, and GitHub workflow publication remain NOT VERIFIED.

## [0.1.1] - 2026-10-15

### Fixed

- Explain low scores caused by length, a single character class, or low estimated
  entropy in human reports and the additive JSON `reasons` list, even without patterns.
- Prepend source PYTHONPATH in module-entry tests; verify them with site-packages
  disabled as well as enabled, without depending on package installation.
- Derive the HIBP user-agent version from the package version.

### Added

- Repository working agreement, bounded STATE checkpoint, and engineering notes.
- pytest-cov development dependency and a 90% statement/branch coverage gate.
- Regression checks for README commands and captured output.
- Python/license badges, package keywords/project URLs, and portfolio rationale.

### Changed

- Support Python 3.14 only; metadata requires `>=3.14,<3.15`.
- Local instructions invoke tools through the explicit virtualenv interpreter.
- Document live HIBP, hosted CI, pipx, publication, and terminal checks as unverified.

## [0.1.0] - 2026-10-15

### Added

- Python 3.14+ src-layout package with the `pwcheck` console and module entry points.
- Stdlib-only charset/entropy estimates, length and pattern score ceilings, and ordered suggestions.
- A bundled memory-curated dictionary of 563 weak-password examples, leetspeak matching, and personal-context checks.
- QWERTY walks, ASCII sequences, repetitions, years/dates, and predictable suffix detection.
- Secure prompting, single-line stdin, explicit-argument warnings, TTY-aware color, and JSON schema version 1.
- Optional HIBP range lookup with prefix-only requests, padding, bounded response reads, and graceful failure handling.
- Unit and CLI regression tests with mocked network access, plus Python 3.14 GitHub Actions CI.
- Installation, scoring, privacy, limitations, and contribution documentation.
