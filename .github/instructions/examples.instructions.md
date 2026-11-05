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
  examples/<script>.py` (no package/`__init__.py` required) and runnable
  fully offline where the library already supports it (e.g.
  `run_pipeline.py` still completes without network/Postgres access,
  because `extract.py`'s enrichment call fails soft).
- A script's docstring should state what it demonstrates and how to run
  it, so it's usable as a copy-paste starting point.
- These files are not covered by `tests/`'s unit-test conventions — they
  are demonstrations, not library code requiring full test coverage. If a
  script accumulates real business logic worth unit-testing, move that
  logic into `src/data_proc/` and add tests there instead.
- Don't add new runtime dependencies solely for an example without
  confirming it's worth adding to `[project.dependencies]` — examples
  should stay runnable with the same environment as the rest of the repo.
