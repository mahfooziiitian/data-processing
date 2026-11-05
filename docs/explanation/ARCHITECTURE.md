---
diataxis: explanation
---

# Architecture

## Overview

This POC implements a classic **batch ETL** (Extract–Transform–Load)
pipeline. It is deliberately simple — a single Python process, no
orchestrator — so the data flow is easy to read end-to-end. The same
structure scales to Airflow/Dagster-orchestrated pipelines, Spark jobs, or
cloud-native services (the `extract` / `transform` / `load` module
boundaries are designed to be swapped out independently).

## Data flow diagram

```text
                    ┌─────────────────────┐
                    │  data/raw/           │
                    │  customers.csv       │
                    │  orders.csv          │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐        ┌──────────────────────┐
                    │   EXTRACT            │◄───────┤ Public demo REST API │
                    │ src/etl/extract.py   │        │ (customer enrichment)│
                    └──────────┬──────────┘        └──────────────────────┘
                               │ pandas DataFrames
                    ┌──────────▼──────────┐
                    │   TRANSFORM          │
                    │ src/etl/transform.py │
                    │ - clean & validate    │
                    │ - compute line totals │
                    │ - enrich customers    │
                    │ - aggregate summary   │
                    └──────────┬──────────┘
                               │ pandas DataFrames
                    ┌──────────▼──────────┐
                    │   LOAD                │
                    │ src/etl/load.py       │
                    └──────────┬──────────┘
                               │ SQLAlchemy
                    ┌──────────▼──────────┐
                    │   PostgreSQL          │
                    │ customers             │
                    │ orders                │
                    │ customer_order_summary│
                    └───────────────────────┘
```

## Component responsibilities

| Component | File | Responsibility |
|---|---|---|
| Config | `src/config.py` | Single source of truth for paths, DB URL, API URL — all overridable via environment variables |
| Extract | `src/etl/extract.py` | Pulls raw data from heterogeneous sources (CSV, REST API) into DataFrames; isolates I/O and failure handling |
| Transform | `src/etl/transform.py` | Pure functions: cleaning, validation, joins, aggregation — no I/O, easy to unit test |
| Load | `src/etl/load.py` | Persists DataFrames via SQLAlchemy; backend-agnostic (Postgres in this demo, SQLite in tests) |
| Pipeline | `src/etl/pipeline.py` | Orchestrates the three stages and logs a run summary |
| Schema | `src/db/schema.sql` | Declarative DDL, auto-applied on Postgres container startup |

## Design decisions

- **DataFrames as the interchange format** between stages keeps each stage
  independently testable and swappable (e.g., replace `extract.py` with a
  Spark DataFrame reader without touching `transform.py`).
- **Resilient API extraction**: the enrichment API call fails soft (logs a
  warning, returns an empty DataFrame) so the demo still runs fully offline.
- **`if_exists="replace"` loads** make the pipeline idempotent and safe to
  re-run repeatedly for demo purposes; a production pipeline would use
  incremental/upsert loads instead (see `docs/explanation/CONCEPTS.md`).
- **Docker Compose for Postgres only** — the Python pipeline runs on the
  host (or in CI) so it's trivial to step through with a debugger.

## Extending this POC

- Swap `extract.py`'s CSV reads for a cloud object store (S3/GCS) or a
  streaming source (Kafka) without touching `transform.py` or `load.py`.
- Introduce an orchestrator (Airflow/Dagster/Prefect) that calls
  `src.etl.pipeline.run()` as a single task, or splits it into per-stage
  tasks with explicit dependencies.
- Add a data-quality layer (e.g., Great Expectations) between transform and
  load to assert invariants before writing to the warehouse.
