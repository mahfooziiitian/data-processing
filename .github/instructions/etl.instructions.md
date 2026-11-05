---
applyTo: "src/data_proc/etl/**/*.py"
---

# ETL library conventions

This package is the reusable **library** half of the project (see the
`src/` vs. `examples/` convention in `.github/copilot-instructions.md`):
every module here must stay importable and testable in isolation, with no
knowledge of how/when it is invoked. Usage/orchestration code (wiring
these functions into a runnable demo) belongs in `examples/`, not here.

- Keep `transform.py` functions **pure** (no I/O, no DB/HTTP calls) — they
  must be testable with small in-memory DataFrame fixtures alone. Put all
  I/O in `extract.py`/`load.py`.
- Stages communicate exclusively via **pandas DataFrames**. Don't introduce
  a different intermediate structure (e.g., dicts, lists of records)
  without updating `extract.py`, `transform.py`, `load.py`, and
  `examples/run_pipeline.py` together.
- External calls in `extract.py` (the enrichment API) must fail soft: catch
  the specific exception, log a warning, and return an empty DataFrame
  rather than raising — the pipeline must still complete fully offline.
- `load.py`'s `load_dataframe()` takes a generic SQLAlchemy `Engine` so it
  works against both Postgres (runtime) and SQLite (tests) — don't add
  Postgres-specific SQL inside it.
- Import settings from `data_proc.config.settings` (the module-level singleton);
  don't read `os.environ` directly in ETL modules.
- If you add/rename a column or table produced by `transform.py`/`load.py`,
  update `src/data_proc/db/schema.sql` to match in the same change.
- Don't add orchestration logic (e.g., a new `run()`-style entry point) to
  this package — add it as a new script under `examples/` instead, and
  have it import from `data_proc.etl`.
