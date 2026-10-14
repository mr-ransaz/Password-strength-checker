# Working agreement

## Session-start protocol

1. Read this file and `STATE.md` before editing anything.
2. Run `git status --short`; stop if the tree is dirty. Do not overwrite or
   discard existing changes.
3. Read `git log -1 --oneline`, confirm the branch and Python version, then
   inspect the relevant code, tests, and documentation.
4. Resolve the release tag mentioned in STATE when checking its release commit.

## Rules

- Use Python 3.14 only. Run every Python/tool command through
  `.\.venv\Scripts\python.exe`, including pip, Ruff, pytest, and the CLI.
  Never use global Python or global tool launchers. Git commands use `git`.
- Runtime dependencies must remain stdlib-only; development-only tools belong
  in the `dev` extra. Explain dependency additions.
- Never log, store, or print a user's password or personal context. Use only
  public synthetic examples in tests and documentation. Do not interpolate
  raw exceptions or matched secret substrings into reports.
- Keep `analyzer.py` pure, deterministic, typed, and free of I/O. Isolate
  network requests in `hibp.py`; tests must mock network access.
- Inspect before editing, make the smallest complete fix, and add meaningful
  regression tests. Do not skip tests or suppress failures to pass a gate.
- README claims and captured outputs must be verified by execution. Explicitly
  distinguish local/mocked checks from unverified external services.
- Make small Conventional Commits with explicit paths. Do not push, rewrite
  history, reset unrelated changes, or move/delete an existing tag.
- Do not delegate to subagents unless the user explicitly requests it.
- Stop after the requested gate and local tag; report open manual checks.

## Gate checklist

- `.\.venv\Scripts\python.exe -m ruff check .`
- `.\.venv\Scripts\python.exe -m ruff format --check .`
- `.\.venv\Scripts\python.exe -m pytest -q` with configured coverage >= 90%.
- `git diff --check`
- Verify every runnable README usage example and its stdout/stderr/exit code.
- Update README, `docs/NOTES.md`, and CHANGELOG with supported claims.
- Update `STATE.md` last (at most 60 lines), recording the actual gate result,
  last implementation commit, and remaining unverified work.
- Commit the checkpoint, create the requested new local release tag, confirm
  a clean tree and tag target, then stop. No push or extra post-gate work.
