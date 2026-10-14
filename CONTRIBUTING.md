# Contributing

Use Python 3.14+ and a virtual environment. Install with `python -m pip install -e ".[dev]"`.

Before submitting a pull request, run:

```console
ruff check .
ruff format .
ruff format --check .
pytest -q
```

Keep runtime code stdlib-only, fully typed, and consistent with the existing src layout. Add focused regression tests for bugs and cover failure paths. Keep analysis deterministic and network access isolated in `hibp.py`; all network tests must use mocks.

Never submit real passwords, personal context, tokens, or private breach records. Use explicitly synthetic fixtures. Do not echo input or raw exceptions in reports or error messages. Describe changes to scores, penalties, public APIs, or the JSON schema in the README and changelog.

Use Conventional Commits and keep pull requests focused. Explain the problem, the change, and the exact verification performed.
