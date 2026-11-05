---
applyTo: "tests/**/*.py"
---

# Test conventions

- Tests must run **without Docker/Postgres**: use an in-memory SQLite
  engine (`create_engine("sqlite:///:memory:")`) for load-layer tests, and
  `unittest.mock.patch` for the external enrichment API call — never hit
  the live network or a real Postgres instance in a test.
- Run via `uv run pytest -v` (not bare `pytest`); `pythonpath = ["."]` in
  `pyproject.toml`'s `[tool.pytest.ini_options]` makes `from src...`
  imports resolve only when invoked from the repo root.
- Transform tests should build small, inline DataFrame fixtures directly in
  the test function rather than reading from `data/raw/` — the sample CSVs
  are for extract-layer tests and manual pipeline runs only.
- One test module per ETL stage (`test_extract.py`, `test_transform.py`,
  `test_load.py`); add new cases to the matching file rather than creating
  parallel test files.
