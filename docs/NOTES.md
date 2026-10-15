# Engineering notes

## Post-v0.2.0 isolation follow-up

- Start: clean main at 2bb15fc; keep v0.2.0 at
  2bb15fc095ea293b7a0fb0c039e9582db40d8488. No version bump or new/moved tag.
- Root cause confirmed by the user: the original .venv inherited system
  site-packages, and the PyInstaller module path also included another project's
  source. Earlier execution/smoke evidence did not establish build isolation.
- **User-reported manual results (PowerShell 7.6.7):** recreated .venv with
  include-system-site-packages=false; rebuilt search path excludes the global
  package directory and unrelated source; one-file/one-folder builds and checksums
  PASS; smoke 9/9 plus PE versions/dictionary/alternate directory PASS; Ruff,
  format check, and pytest PASS; Explorer double-click PASS; no local-build
  SmartScreen or antivirus warning observed. These were not rerun as human checks
  by the agent and do not verify downloaded assets or another machine.
- **Observed in this follow-up:** Python 3.14.0, pyvenv.cfg explicitly false, no
  PYTHONPATH, and PowerShell 7.6.5 in the agent command session. The user-reported
  PowerShell 7.6.7 result is kept separate from this session's measurements.
- Add a stdlib-only preflight before any PyInstaller import or build/dist cleanup.
  Run it as a script with -I -S: Python 3.14 preserves the venv prefix under -S,
  while site initialization and PYTHONPATH import injection are disabled for the
  guard. os.environ still exposes the presence of PYTHONPATH for rejection.
- Pure logic requires exactly one include-system-site-packages=false setting;
  missing, duplicate, true, and unknown values fail closed. Reject any PYTHONPATH
  key case-insensitively, including empty values. Diagnostics never reveal values.
- Guard acceptance and deliberate PYTHONPATH rejection were executed; rejection
  occurred before cleanup and existing artifact checksums were unchanged.
- In the agent PowerShell 7.6.5 session, passing $null to the .NET environment
  setter left an empty PYTHONPATH, which the guard correctly rejected. Verified
  removal uses `if (Test-Path Env:\PYTHONPATH) { Remove-Item Env:\PYTHONPATH }`;
  the subsequent isolated preflight exits 0. This removes only the process variable.
- [Clean-venv recreation](../README.md#recreate-a-clean-build-environment): deactivate,
  back up old .venv outside build/dist, manually bootstrap a fresh default-isolated
  Python 3.14 .venv, do not copy old packages/path files, remove process PYTHONPATH,
  run the isolated preflight, then install through .venv Python. Recreation itself
  was already performed by the user and was not repeated by this follow-up.
- No full executable rebuild is needed for this preflight-only change; user-reported
  clean-build/smoke evidence above is not relabeled as an agent-run build.
- Follow-up gate: Ruff lint/format PASS; 283 tests PASS, including 30 added cases
  for pure validation/guard entry points; application statement/branch coverage
  remains 98.66%. README command verification and editable dev/build install PASS.
- Python-free Windows machine: **NOT VERIFIED**; there is no second Windows machine,
  and the Kali VM is not applicable. Git push, GitHub CI, release workflow, publication,
  and downloaded-asset checks remain **NOT VERIFIED**. No push is authorized.

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
- Local Windows 11 x64 / Python 3.14.0 build: PASS with PyInstaller 6.22.3 and
  hooks-contrib 2026.8. Both executable file/product versions are 0.2.0.
- Smoke gate: PASS for nine checks across one-file, one-folder, and unzipped folder:
  version 0, weak stdin 1, strong stdin 0. All run outside the repository root with
  PYTHONHOME/PYTHONPATH/VIRTUAL_ENV removed and PATH restricted to System32. Full
  synthetic password values never appear in captured stdout/stderr. Known weak
  input confirms the bundled dictionary is loaded. Both SHA-256 entries match.
- The ZIP includes the complete folder and dictionary; one-file has no embedded
  Authenticode certificate (checked through the PE security directory). It is unsigned.
- Build warning files were inspected: they list platform-conditional stdlib imports
  and an import-graph collections.abc warning; the actual Windows CLI imports and
  local smoke checks succeed. No warnings or checks were suppressed.
- Generated specs, version text, caches, executables, ZIP, and checksums remain
  under ignored build/dist paths. Cleanup validates absolute targets and rejects
  reparse points. No user passwords are written by any build/smoke code.
- The release workflow has a read-only build job and a separate `contents: write`
  release job. setup-python's selected Python 3.14 bootstraps the job-local .venv;
  subsequent Python commands use .venv. Local commands never use global Python.
- At the original checkpoint, Explorer/SmartScreen results were not verified;
  the user-reported local checks above supersede that status for that build only.
  The release workflow, downloaded-asset behavior, and Python-free machine remain
  NOT VERIFIED.

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
- Package metadata restricts compatibility to `>=3.14,<3.15`; version 0.2.0 is
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
- v0.2.0 local suite before final checkpoint: 253 passing tests and 98.66% combined
  statement/branch coverage. All CLI branches, including the frozen loop, are covered.
- HIBP transport is mocked in tests; no real passwords are sent to the service.

## Commands for the local gate

Run from the project root with the explicit virtualenv interpreter:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
.\scripts\build_exe.ps1
.\scripts\smoke_exe.ps1
git diff --check
```

Lint and formatting must pass, pytest must pass with at least 90% total coverage,
and diff checking must produce no output. STATE records the final gate result.

## Open items and verification limits

- Live HIBP check: **NOT verified**.
- GitHub-hosted CI: **NOT verified**; a checked-in workflow is not execution proof.
- GitHub Windows release workflow / publication: **NOT verified**; it has not run.
- Explorer double-click: **user-reported PASS** on the clean local v0.2.0 build,
  without SmartScreen/antivirus warning. Downloaded-asset/other-machine behavior:
  **NOT VERIFIED**. No separate live terminal measurement was made by the agent.
- Execution on a Windows machine without Python, downloaded assets, pipx installation,
  package-index publication, and remote placeholder URLs: **NOT VERIFIED**.
- No pushes or remote releases are authorized for this checkpoint.
