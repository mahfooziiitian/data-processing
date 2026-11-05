# Data Processing POC & Demo

A small, self-contained proof-of-concept demonstrating core **data
engineering concepts**: multi-source extraction, cleaning/transformation,
aggregation, and loading into a relational database — the classic **ETL**
pattern — using Python, pandas, and PostgreSQL.

This site documents the project. For the quickstart and repository layout,
see the sections below; for hands-on setup steps see
[Setup Guide](tutorials/setup.md).

## What it does

The pipeline (`examples/run_pipeline.py`) runs three stages:

1. **Extract** — reads `customers.csv` and `orders.csv` from `data/raw/`, and
   optionally fetches supplementary profile data from a public demo REST API.
2. **Transform** — cleans and validates records, computes order line totals,
   and builds a per-customer order summary (order count, total spend, last
   order date).
3. **Load** — writes the resulting tables into PostgreSQL.

Continue to [Architecture](explanation/architecture.md) for a data-flow
diagram, or [Concepts](explanation/concepts.md) for the data engineering
ideas this demo illustrates.

### Kappa architecture demo

`examples/run_kappa_stream.py` + `src/data_proc/kappa/` demonstrate the
**Kappa architecture** pattern alongside the batch pipeline above: a single
unified stream-processing path (event log → fold into state → upsert) that
handles incremental runs and full historical **replay** identically. See
[How to run the Kappa demo](how-to/run-kappa-demo.md) for a walkthrough and
[Architecture → Kappa architecture demo](explanation/architecture.md#kappa-architecture-demo)
for the design rationale.

### Lambda architecture demo

`examples/run_lambda_architecture.py` + `src/data_proc/lambda_arch/`
demonstrate the **Lambda architecture** pattern: a slow, always-correct
batch layer and a fast, gap-covering speed layer, merged at query time by
a serving layer. See
[How to run the Lambda demo](how-to/run-lambda-demo.md) for a walkthrough
and
[Architecture → Lambda architecture demo](explanation/architecture.md#lambda-architecture-demo)
for the design rationale.

### Data Mesh architecture demo

`examples/run_data_mesh.py` + `src/data_proc/data_mesh/` demonstrate the
**Data Mesh** pattern: two independent domains (customers, orders) each
publish their own data product through a shared, self-serve catalog, and
a consumer discovers and joins both products without either domain
knowing the consumer exists. See
[How to run the Data Mesh demo](how-to/run-data-mesh-demo.md) for a
walkthrough and
[Architecture → Data Mesh architecture demo](explanation/architecture.md#data-mesh-architecture-demo)
for the design rationale.

## Quickstart

```bash
# 1. Start PostgreSQL (applies sql/schema.sql automatically)
docker compose up -d

# 2. Install dependencies with uv
uv sync

# 3. Run the pipeline
uv run python examples/run_pipeline.py

# 4. Inspect the results
docker compose exec postgres psql -U postgres -d data_processing_demo \
  -c "SELECT * FROM customer_order_summary ORDER BY total_spent DESC;"
```

## Repository layout

```text
.
├── data/raw/                     Sample input CSVs (customers, orders)
├── src/data_proc/config.py       Centralized, environment-driven settings
├── src/data_proc/etl/            Reusable extract.py / transform.py / load.py library
├── src/data_proc/kappa/          Event log, checkpoint, state, fold (Kappa demo library)
├── src/data_proc/lambda_arch/    Batch/speed/serving layers (Lambda demo library)
├── src/data_proc/data_mesh/      Contract/governance/catalog + two domains (Data Mesh demo library)
├── examples/run_pipeline.py      Demo script: wires extract -> transform -> load
├── examples/run_kappa_stream.py  Demo script: single stream path + replay
├── examples/run_lambda_architecture.py  Demo script: batch + speed + serving layers
├── examples/run_data_mesh.py     Demo script: publish two domains + self-serve consumer join
├── sql/schema.sql                PostgreSQL DDL, auto-applied by docker-compose
├── tests/                        pytest unit tests for each ETL/kappa/lambda/data_mesh module
├── docker-compose.yml            Local PostgreSQL for the demo
└── docs/                         This documentation site (MkDocs)
```
