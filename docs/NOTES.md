# Engineering notes

## Windows executable phase (v0.2.0)

- Session starts from clean main at 1e87110, preserving the committed README URL.
- On 2026-10-15, the current stable PyInstaller release is **6.22.3** (2026-09-12),
  verified against [PyPI](https://pypi.org/project/pyinstaller/6.22.3/) and the
  [official changelog](https://pyinstaller.org/en/stable/CHANGES.html). The changelog
  records Python 3.14 support in 6.15.0; current release metadata also lists 3.14.
- Pin PyInstaller 6.22.3 in the optional `build` extra, separate from `dev` and
  empty runtime dependencies. It packages Python into Windows artifacts; it is
  not imported by the password analyzer or CLI.
- Use console-mode one-file and one-folder builds, explicitly include the public
  dictionary, disable UPX, and generate Windows version resources from the package
  version. Use a custom icon only if assets/pwcheck.ico actually exists.
- No-argument frozen runs with terminal stdin/stdout will repeat secure getpass
  prompts until empty input. Empty ends this convenience session with exit 0;
  noninteractive or argument-driven runs retain the existing 0/1/2 behavior.
- Local build and executable smoke gate: pending. The GitHub release workflow,
  double-click behavior, SmartScreen behavior, and execution on a Python-free
  machine are NOT verified.

## Decisions

- Runtime code remains stdlib-only. pytest, pytest-cov, and Ruff are development
  tools; pytest-cov enforces a 90% minimum statement/branch coverage gate.
- Python 3.14 is the supported series. Local commands must use
  `.\.venv\Scripts\python.exe`; Git uses its own command.
- Low-score explanations belong in the pure analyzer, with password-free
  metadata consumed by both human and JSON formatters. Character classes help
  explain the estimated search space; mixed classes are not a scoring rule.
- JSON schema version 1 gains an additive `reasons` list. An empty list is valid
  for good/strong inputs. Existing scores and the shape of findings are unchanged.
- Source-based subprocess tests prepend the absolute `src` path to
  PYTHONPATH and preserve existing entries, without depending on installation.
  They also execute with `-S` and a tests-directory working directory, proving
  imports work without site-packages or the project root on the search path.
- The dictionary is memory-curated, unranked, and contains 563 examples.
- Entropy and crack time are heuristics. Meaningful phrases can be overestimated;
  no score guarantees safety. Scores and penalties are unchanged by report fixes.
- STATE records a predecessor commit and a release tag reference: a commit cannot
  contain its own hash. Update STATE last and resolve the tag for the release HEAD.
- Package metadata restricts compatibility to `>=3.14,<3.15`; version 0.1.1 is
  shared with the CLI and the HIBP user-agent. Project URLs remain placeholders.

## Verification evidence

- Session started from a clean main at 79cc3af on Python 3.14.0.
- Baseline: 200 passing tests; 98.81% statement coverage.
- v0.1.1 local suite: 227 passing tests; 98.61% combined statement/branch coverage.
  The pure analyzer and human/JSON report modules each have 100% measured coverage.
  The 90% threshold is configured in pytest and coverage; no modules are excluded.
- Parent coverage does not collect subprocess execution. `__main__.py` is reported
  uncovered despite being exercised by subprocess tests; an unreachable time-unit
  guard is the other uncovered statement. These gaps are not hidden or waived.
- README tests compare all six usage examples, JSON, stderr warning, version, and
  exit codes against actual module executions. Inputs are public synthetic fixtures.
- HIBP transport is mocked in tests; no real passwords are sent to the service.

## Commands for the local gate

Run from the project root with the explicit virtualenv interpreter:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

Lint and formatting must pass, pytest must pass with at least 90% total coverage,
and diff checking must produce no output. STATE records the final gate result.

## Open items and verification limits

- Live HIBP check: **NOT verified**.
- GitHub-hosted CI: **NOT verified**; a checked-in workflow is not execution proof.
- pipx installation, package-index publication, remote placeholder URLs, and a live
  interactive no-echo terminal prompt: **NOT verified**.
- No pushes or remote releases are authorized for this checkpoint.
