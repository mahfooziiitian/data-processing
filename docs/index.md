# Data Processing POC & Demo

A small, self-contained proof-of-concept demonstrating core **data
engineering concepts**: multi-source extraction, cleaning/transformation,
aggregation, and loading into a relational database — the classic **ETL**
pattern — using Python, pandas, and PostgreSQL.

This site documents the project. For the quickstart and repository layout,
see the sections below; for hands-on setup steps see
[Setup Guide](tutorials/setup.md).

## What it does

The pipeline (`src/etl/pipeline.py`) runs three stages:

1. **Extract** — reads `customers.csv` and `orders.csv` from `data/raw/`, and
   optionally fetches supplementary profile data from a public demo REST API.
2. **Transform** — cleans and validates records, computes order line totals,
   and builds a per-customer order summary (order count, total spend, last
   order date).
3. **Load** — writes the resulting tables into PostgreSQL.

Continue to [Architecture](explanation/architecture.md) for a data-flow
diagram, or [Concepts](explanation/concepts.md) for the data engineering
ideas this demo illustrates.

## Quickstart

```bash
# 1. Start PostgreSQL (applies src/db/schema.sql automatically)
docker compose up -d

# 2. Install dependencies with uv
uv sync

# 3. Run the pipeline
uv run python -m src.etl.pipeline

# 4. Inspect the results
docker compose exec postgres psql -U postgres -d data_processing_demo \
  -c "SELECT * FROM customer_order_summary ORDER BY total_spent DESC;"
```

## Repository layout

```text
.
├── data/raw/            Sample input CSVs (customers, orders)
├── src/config.py        Centralized, environment-driven settings
├── src/db/schema.sql    PostgreSQL DDL, auto-applied by docker-compose
├── src/etl/             extract.py / transform.py / load.py / pipeline.py
├── tests/               pytest unit tests for each ETL stage
├── docker-compose.yml   Local PostgreSQL for the demo
└── docs/                This documentation site (MkDocs)
```
