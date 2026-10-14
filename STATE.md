# Repository state

- Version: 0.2.0 (Python 3.14 only; Windows x64 executable phase)
- Branch: main
- Last checked commit before this checkpoint: 70ef8948365e944ea72faf1f85ef5faa7f086fef
- Commit purpose: docs: document Windows downloads and local build evidence
- Release commit: resolve the local annotated tag v0.2.0^{commit}.
- Status: gate passed; stop here for manual checks. No push or history rewrite.
- STATE was updated last; the following checkpoint commit and tag identify HEAD.

## Verification

- Local interpreter: .\.venv\Scripts\python.exe, Python 3.14.0 on Windows 11 x64.
- Ruff lint: PASS; Ruff format --check: PASS.
- pytest -q: 253 passed; combined statement/branch coverage 98.66% (minimum 90%).
- git diff --check: PASS; no whitespace errors.
- README: six usage examples, JSON, warning, and version match actual output.
- Frozen terminal loop: fake-based tests PASS; normal scripted scores/exits unchanged.
- Module tests pass with site-packages disabled and source PYTHONPATH prepended.
- Editable v0.2.0 dev/build installation: PASS; PyInstaller 6.22.3 support verified.
- Local clean one-file and one-folder Windows builds: PASS; no UPX.
- Both PE file/product versions: 0.2.0, generated from package metadata.
- Smoke: all nine version/weak/strong invocations PASS; no password echo.
- Smoke covers one-file, one-folder, and extracted ZIP from alternate working dir.
- Bundled dictionary, both SHA-256 entries, and restricted Python environment: PASS.
- Ignored artifacts: dist/pwcheck.exe, dist/pwcheck-folder.zip, dist/SHA256SUMS.txt.
- Unsigned artifact confirmed through PE certificate-directory inspection.
- Release workflow PowerShell blocks parse; GitHub execution NOT verified.
- Subprocess coverage is not collected; reported gaps are documented in NOTES.

## Open items / NOT verified

- Live HIBP check: NOT verified.
- GitHub-hosted CI: NOT verified.
- GitHub Windows release workflow and release publication: NOT verified (not run).
- pipx installation and package-index publication: NOT verified.
- Explorer double-click and actual terminal no-echo/repeat: NOT manually verified.
- SmartScreen/antivirus behavior and a machine without Python: NOT verified.
- Placeholder project URLs and remote badges: NOT verified.
- Runtime-only wheel installation for v0.2.0: NOT verified in this session.
