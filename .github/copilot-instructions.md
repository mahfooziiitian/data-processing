# Copilot Instructions for data-processing

Python ETL proof-of-concept: CSV + REST API → pandas transform → PostgreSQL,
used as a learning/demo reference for data engineering concepts.

## Commands

All Python commands go through [uv](https://docs.astral.sh/uv/) — there is
no activated virtualenv convention; prefix with `uv run`.

```bash
uv sync --all-groups          # install runtime + dev (pytest) + docs (mkdocs) deps
docker compose up -d           # start local Postgres (auto-applies src/data_proc/db/schema.sql)
uv run python -m data_proc.etl.pipeline   # run the full ETL pipeline
uv run pytest -v                    # run all tests
uv run pytest tests/test_transform.py::test_clean_orders_drops_missing_customer_and_computes_line_total  # single test
uv run --group docs mkdocs serve          # preview docs site at :8000 with live reload
uv run --group docs mkdocs build --strict # build docs, fail on warnings
```

Equivalent `make` targets exist: `setup`, `up`, `down`, `test`, `run`, `docs`,
`docs-serve`, `clean`.

Tests do **not** require Docker/Postgres running — `tests/test_load.py` uses
an in-memory SQLite engine, and `tests/test_extract.py` mocks the external
API call via `unittest.mock.patch`.

## Architecture

Three-stage ETL pipeline (`src/data_proc/etl/`), orchestrated by
`pipeline.py`, with each stage in its own module so they can be
tested/swapped independently:

- **`extract.py`** — reads `data/raw/customers.csv` and `orders.csv`, and
  calls a public demo REST API (`jsonplaceholder.typicode.com`) for
  enrichment. The API call fails soft (logs a warning, returns an empty
  DataFrame) so the pipeline still completes fully offline — preserve this
  behavior if you touch extraction.
- **`transform.py`** — pure functions only (no I/O): cleaning/validation,
  computing `line_total`, joining enrichment data, and aggregating into
  `customer_order_summary`. Keep new transform logic pure so it stays
  unit-testable with small in-memory DataFrame fixtures.
- **`load.py`** — generic `load_dataframe(df, table_name, engine)` over any
  SQLAlchemy engine; used with Postgres in the app and SQLite in tests.
  Loads use `if_exists="replace"` to keep repeated pipeline runs idempotent
  for demo purposes (not an upsert/merge — don't assume incremental-load
  semantics elsewhere).

All stages pass plain **pandas DataFrames** between each other — this is
the interchange format; don't introduce a different intermediate structure
without updating all three stages.

Config (`src/data_proc/config.py`) is a single frozen `Settings` dataclass
sourced from env vars (`DATABASE_URL`, `ENRICHMENT_API_URL`,
`REQUEST_TIMEOUT_SECONDS`), instantiated once as the module-level `settings`
singleton and imported from there — don't read `os.environ` directly in
other modules.

`src/data_proc/db/schema.sql` is the source of truth for table DDL and is
applied automatically by the Postgres container on first startup
(`docker-entrypoint-initdb.d`). If you change table shape in
`transform.py`/`load.py`, update `schema.sql` to match, and note that a
schema change requires `docker compose down -v` (drops the volume) before
`up -d` re-applies it.

Full architecture write-up and diagram: `docs/explanation/architecture.md`.
Conceptual rationale for design choices: `docs/explanation/concepts.md`.

## Conventions

- The installable root package is `data_proc`, living in the src layout at
  `src/data_proc/` (`pyproject.toml`'s `[tool.hatch.build.targets.wheel]`
  maps `src/data_proc` to the `data_proc` package). Imports are rooted at
  the package as `data_proc.etl.*`, `data_proc.db.*`, `data_proc.config`
  (not relative imports) — `uv sync` installs it in editable mode, so
  `import data_proc` resolves from any working directory once synced.
- `pyproject.toml` declares a standard `[build-system]`
  (hatchling) so `data_proc` installs as an editable package; this is
  still a demo application, not a published library — don't add
  publishing/release automation without reason.
- Dependency groups: runtime deps under `[project.dependencies]`, test deps
  under `dependency-groups.dev`, docs deps under `dependency-groups.docs`.
  Add new deps with `uv add <pkg>`, `uv add --dev <pkg>`, or
  `uv add --group docs <pkg>` respectively (not by hand-editing
  `pyproject.toml`), then re-run `uv sync --all-groups`.
- Docs under `docs/` are both human-readable Markdown and the MkDocs site
  source (`mkdocs.yml` → `docs_dir: docs`). Adding a new doc page requires
  also adding it to the `nav:` list in `mkdocs.yml`.
- Documentation pages follow the Diátaxis folders and lowercase filename
  rules documented in `.github/instructions/docs.instructions.md`. Preserve
  the Material theme features `navigation.tabs`, `toc.integrate`, and
  `navigation.footer` in `mkdocs.yml`; do not remove them during unrelated
  edits.
- For requests to enhance, enrich, rewrite, or polish documentation, use the
  `.github/skills/documentation-content-enhancer/SKILL.md` workflow before
  editing. Keep repository facts verified and label hypothetical platform
  examples clearly.
- For documentation changes, run `uv run --group docs mkdocs build --strict`,
  `python3 .github/skills/diataxis-docs-audit/check_diataxis.py`, and
  `git diff --check`. Do not commit the generated `site/` directory.
