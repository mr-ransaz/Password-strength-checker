# Changelog

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
