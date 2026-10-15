# Repository state

- Version: 0.2.0 (Python 3.14 only; post-release build-isolation follow-up)
- Branch: main
- Last checked commit before this follow-up: 2bb15fc095ea293b7a0fb0c039e9582db40d8488
- Base purpose: docs: record the v0.2.0 executable verification gate
- Release tag v0.2.0 stays at that base commit; this follow-up has no new tag.
- Status: gate passed; single follow-up commit, then stop. No push/history rewrite.
- STATE was updated last; the following commit is an untagged descendant of v0.2.0.

## Verification

- Agent: .\.venv\Scripts\python.exe, Python 3.14.0; PowerShell 7.6.5.
- Observed configuration: system site-packages false; PYTHONPATH absent.
- Ruff lint: PASS; Ruff format --check: PASS.
- pytest -q: 283 passed; application statement/branch coverage 98.66% (minimum 90%).
- Added 30 test cases for pure validation and preflight entry points.
- git diff --check: PASS; no whitespace errors.
- README: six usage examples, JSON, warning, and version match actual output.
- Clean isolated preflight: PASS; editable dev/build installation: PASS.
- Deliberate PYTHONPATH rejection through build_exe.ps1: PASS before cleanup.
- Existing artifact checksums unchanged; full executable rebuild not rerun here.
- Guard uses -I -S before loading site/.pth files; diagnostics never print values.
- User reports (PowerShell 7.6.7): clean-venv rebuild/checksums and smoke 9/9 PASS,
  including PE versions, dictionary, and alternate directory; lint/format/tests PASS.
- User reports recreated .venv removed global packages/unrelated source from build path.
- User reports Explorer double-click PASS with no local SmartScreen/antivirus warning.
- Environment recreation and human checks were not repeated by the agent.

## Open items / NOT verified

- Live HIBP check: NOT verified.
- GitHub-hosted CI: NOT verified.
- GitHub Windows release workflow and release publication: NOT verified (not run).
- pipx installation and package-index publication: NOT verified.
- Downloaded-asset checks and downloaded-asset SmartScreen/antivirus behavior: NOT VERIFIED.
- Windows machine without Python: NOT VERIFIED; Kali VM is not applicable.
- No separate agent measurement of live terminal no-echo/repeat.
- Placeholder project URLs and remote badges: NOT verified.
- Runtime-only wheel installation for v0.2.0: NOT verified in this session.
