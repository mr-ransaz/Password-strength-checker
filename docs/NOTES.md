# Engineering notes

## Decisions

- Runtime code remains stdlib-only. pytest, pytest-cov, and Ruff are development
  tools; pytest-cov is being added to enforce a 90% minimum coverage gate.
- Python 3.14 is the supported series. Local commands must use
  `.\.venv\Scripts\python.exe`; Git uses its own command.
- Low-score explanations belong in the pure analyzer, with password-free
  metadata consumed by both human and JSON formatters. Character classes help
  explain the estimated search space; mixed classes are not a scoring rule.
- Source-based subprocess tests will prepend the absolute `src` path to
  PYTHONPATH and preserve existing entries, without depending on installation.
- The dictionary is memory-curated, unranked, and contains 563 examples.
- Entropy and crack time are heuristics. Meaningful phrases can be overestimated;
  no score guarantees safety. Scores and penalties are unchanged by report fixes.
- STATE records a predecessor commit and a release tag reference: a commit cannot
  contain its own hash. Update STATE last and resolve the tag for the release HEAD.

## Verification evidence

- Session started from a clean main at 79cc3af on Python 3.14.0.
- Baseline: 200 passing tests; 98.81% statement coverage. Release gate pending.
- HIBP transport is mocked in tests; no real passwords are sent to the service.

## Open items and verification limits

- Live HIBP check: **NOT verified**.
- GitHub-hosted CI: **NOT verified**; a checked-in workflow is not execution proof.
- pipx installation, package-index publication, remote placeholder URLs, and a live
  interactive no-echo terminal prompt: **NOT verified**.
- No pushes or remote releases are authorized for this checkpoint.
