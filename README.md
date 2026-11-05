# Data Processing POC & Demo

A small, self-contained proof-of-concept repository demonstrating core
**data engineering concepts**: multi-source extraction, cleaning/transformation,
aggregation, and loading into a relational database — the classic **ETL**
pattern — using Python, pandas, and PostgreSQL.

This repo is intentionally lightweight so it can serve as:

- A **learning reference** for ETL/data-pipeline concepts.
- A **starting template** for real data-processing projects.
- A **demo** you can run end-to-end in minutes with Docker Compose.

## What it does

The pipeline (`examples/run_pipeline.py`) runs three stages:

1. **Extract** — reads `customers.csv` and `orders.csv` from `data/raw/`, and
   optionally fetches supplementary profile data from a public demo REST API
   (`https://jsonplaceholder.typicode.com/users`).
2. **Transform** — cleans and validates records (trims/normalizes fields,
   drops orders with missing customer references, computes order line
   totals), then builds a per-customer order summary (order count, total
   spend, last order date).
3. **Load** — writes the resulting `customers`, `orders`, and
   `customer_order_summary` tables into PostgreSQL.

See [`docs/explanation/architecture.md`](docs/explanation/architecture.md) for
a diagram and data flow details, and
[`docs/explanation/concepts.md`](docs/explanation/concepts.md) for the data
engineering concepts this demo illustrates.

## Quickstart

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency
management.

```bash
# 1. Start PostgreSQL (applies src/data_proc/db/schema.sql automatically)
docker compose up -d

# 2. Install dependencies (creates .venv automatically)
uv sync --all-groups

# 3. Run the pipeline
uv run python examples/run_pipeline.py

# 4. Inspect the results
docker compose exec postgres psql -U postgres -d data_processing_demo \
  -c "SELECT * FROM customer_order_summary ORDER BY total_spent DESC;"
```

Or, with `make`:

```bash
make setup   # uv sync (installs runtime, dev, and docs dependencies)
make up      # start postgres
make run     # run the pipeline
make test    # run the test suite
make docs    # build the documentation site (docs/ -> site/)
make down    # stop postgres
```

Full setup instructions, including troubleshooting, are in
[`docs/tutorials/setup.md`](docs/tutorials/setup.md).

## Documentation site

The contents of `docs/` are also published as a browsable
[MkDocs](https://www.mkdocs.org/) site (Material theme). Preview it locally:

```bash
make docs-serve   # serves http://127.0.0.1:8000 with live reload
```

## Repository layout

```
.
├── data/raw/                     Sample input CSVs (customers, orders)
├── data/processed/               Reserved for pipeline output artifacts (gitignored)
├── src/data_proc/config.py       Centralized, environment-driven settings
├── src/data_proc/db/schema.sql   PostgreSQL DDL, auto-applied by docker-compose
├── src/data_proc/etl/            Reusable extract.py / transform.py / load.py library
├── examples/run_pipeline.py      Demo script: wires extract -> transform -> load
├── tests/                        pytest unit tests for each ETL stage
├── docker-compose.yml            Local PostgreSQL for the demo
├── docs/                         Architecture, concepts, and setup docs (MkDocs site)
├── mkdocs.yml                    MkDocs site configuration
└── pyproject.toml                uv-managed project metadata and dependencies
```

## Testing

```bash
uv run pytest -v
```

Tests cover extraction (CSV + resilient API fallback), transformation
(cleaning, validation, aggregation), and loading (against an in-memory
SQLite engine so no live database is required).

## License

This is a demo/POC repository for learning and experimentation purposes.
