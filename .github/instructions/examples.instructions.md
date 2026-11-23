---
applyTo: "examples/**/*.py"
---

# Examples conventions

`examples/` holds usage, demo, and exploration code — see the `src/` vs.
`examples/` convention in `.github/copilot-instructions.md`. Files here
show *how* to use the `data_proc` library; they are not part of it.

- Scripts must import from the installed `data_proc` package
  (`from data_proc.etl import extract, transform, load`, etc.) rather than
  duplicating or reimplementing logic that belongs in `src/data_proc/`.
  If a script needs new reusable logic, add it to the library and import
  it here instead of inlining it.
- Keep each script runnable standalone with `uv run python
  examples/<script>.py` (no package/`__init__.py` required). Preserve
  fail-soft API enrichment so the ETL demo can run without internet; it
  still requires a reachable database.
- A script's docstring should state what it demonstrates and how to run
  it, so it's usable as a copy-paste starting point.
- Test consequential orchestration behavior with isolated files and an
  in-memory database or mocks, especially checkpointing and write order.
  Move reusable business logic into `src/data_proc/` and test it there.
- Don't add new runtime dependencies solely for an example without
  confirming it's worth adding to `[project.dependencies]` — examples
  should stay runnable with the same environment as the rest of the repo.
