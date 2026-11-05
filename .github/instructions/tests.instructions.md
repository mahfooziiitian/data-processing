---
applyTo: "tests/**/*.py"
---

# Test conventions

- Tests must run **without Docker/Postgres**: use an in-memory SQLite
  engine (`create_engine("sqlite:///:memory:")`) for load-layer tests, and
  `unittest.mock.patch` for the external enrichment API call — never hit
  the live network or a real Postgres instance in a test.
- Run via `uv run pytest -v` (not bare `pytest`); `data_proc` is an
  installed editable package (`src/data_proc`, see
  `[tool.hatch.build.targets.wheel]` in `pyproject.toml`), so
  `from data_proc...` imports resolve regardless of the invoking
  directory, as long as `uv sync` has been run.
- Transform tests should build small, inline DataFrame fixtures directly in
  the test function rather than reading from `data/raw/` — the sample CSVs
  are for extract-layer tests and manual pipeline runs only.
- One test module per ETL stage (`test_extract.py`, `test_transform.py`,
  `test_load.py`); add new cases to the matching file rather than creating
  parallel test files.
