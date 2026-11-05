---
applyTo: "src/etl/**/*.py"
---

# ETL module conventions

- Keep `transform.py` functions **pure** (no I/O, no DB/HTTP calls) — they
  must be testable with small in-memory DataFrame fixtures alone. Put all
  I/O in `extract.py`/`load.py`.
- Stages communicate exclusively via **pandas DataFrames**. Don't introduce
  a different intermediate structure (e.g., dicts, lists of records)
  without updating `extract.py`, `transform.py`, `load.py`, and
  `pipeline.py` together.
- External calls in `extract.py` (the enrichment API) must fail soft: catch
  the specific exception, log a warning, and return an empty DataFrame
  rather than raising — the pipeline must still complete fully offline.
- `load.py`'s `load_dataframe()` takes a generic SQLAlchemy `Engine` so it
  works against both Postgres (runtime) and SQLite (tests) — don't add
  Postgres-specific SQL inside it.
- Import settings from `src.config.settings` (the module-level singleton);
  don't read `os.environ` directly in ETL modules.
- If you add/rename a column or table produced by `transform.py`/`load.py`,
  update `src/db/schema.sql` to match in the same change.
