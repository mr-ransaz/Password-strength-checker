# Repository state

- Version: 0.1.1 (Python 3.14 only)
- Branch: main
- Last checked commit before this checkpoint: c4a19ae979dac594f49e198ba66e4efbcafef014
- Commit purpose: docs: verify v0.1.1 examples and record verification limits
- Release commit: resolve the local annotated tag v0.1.1^{commit}.
- Status: gate passed; stop here for manual checks. No push or history rewrite.
- STATE was updated last; the following checkpoint commit and tag identify HEAD.

## Verification

- Local interpreter: .\.venv\Scripts\python.exe, Python 3.14.0 on Windows.
- Ruff lint: PASS; Ruff format --check: PASS.
- pytest -q: 227 passed; combined statement/branch coverage 98.61% (minimum 90%).
- git diff --check: PASS; no whitespace errors.
- README: six usage examples, JSON, warning, and version match actual output.
- Short digits-only human/JSON reports show all three reasons; scores unchanged.
- Module tests pass with site-packages disabled and source PYTHONPATH prepended.
- Editable v0.1.1 dev installation and version command: PASS.
- Subprocess coverage is not collected; reported gaps are documented in NOTES.

## Open items / NOT verified

- Live HIBP check: NOT verified.
- GitHub-hosted CI: NOT verified.
- pipx installation and package-index publication: NOT verified.
- Live interactive terminal no-echo behavior: NOT manually verified.
- Placeholder project URLs and remote badges: NOT verified.
- Runtime-only wheel installation for v0.1.1: NOT verified in this session.
