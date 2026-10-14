# Contributing

Use Python 3.14 only and the existing `.venv`. Read AGENTS.md and STATE.md,
then confirm a clean tree and the last commit before editing. Run Python tools
only through `.\.venv\Scripts\python.exe`; never use global tool launchers.
The README describes the development installation and its prerequisites.

Before submitting a pull request, run:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m pytest -q
git diff --check
```

pytest measures statement/branch coverage and fails below 90%. Verify README
examples and update README, docs/NOTES.md, and CHANGELOG; update STATE last.
Use synthetic fixtures and preserve existing history. Do not push during a
local checkpoint task or claim live HIBP/hosted CI verification from mocks.

Keep runtime code stdlib-only, fully typed, and consistent with the existing src layout. Add focused regression tests for bugs and cover failure paths. Keep analysis deterministic and network access isolated in `hibp.py`; all network tests must use mocks.

Never submit real passwords, personal context, tokens, or private breach records. Use explicitly synthetic fixtures. Do not echo input or raw exceptions in reports or error messages. Describe changes to scores, penalties, public APIs, or the JSON schema in the README and changelog.

Use Conventional Commits and keep pull requests focused. Explain the problem, the change, and the exact verification performed.
