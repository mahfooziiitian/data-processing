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

### Kappa architecture demo

`examples/run_kappa_stream.py` + `src/data_proc/kappa/` demonstrate the
**Kappa architecture** pattern alongside the batch pipeline above: a single
stream-processing path (append-only event log → fold into state → upsert)
that handles both incremental runs and full historical **replay** with no
separate batch/speed layers to keep in sync.

```bash
uv run python examples/run_kappa_stream.py --seed     # seed sample order events
uv run python examples/run_kappa_stream.py             # process new events (incremental)
uv run python examples/run_kappa_stream.py --cancel 1001  # append & process a cancellation
uv run python examples/run_kappa_stream.py --replay    # reprocess the ENTIRE log from scratch
```

See [`docs/how-to/run-kappa-demo.md`](docs/how-to/run-kappa-demo.md) for a
full walkthrough and
[`docs/explanation/architecture.md`](docs/explanation/architecture.md#kappa-architecture-demo)
for the design rationale.

### Lambda architecture demo

`examples/run_lambda_architecture.py` + `src/data_proc/lambda_arch/`
demonstrate the **Lambda architecture** pattern: a slow, always-correct
**batch layer** and a fast, gap-covering **speed layer**, merged at query
time by a **serving layer** — the two-path design Kappa was proposed to
replace.

```bash
uv run python examples/run_lambda_architecture.py --batch          # batch layer: full recompute
uv run python examples/run_lambda_architecture.py --seed-speed 3   # simulate new orders in the gap
uv run python examples/run_lambda_architecture.py                  # speed layer + serving merge
uv run python examples/run_lambda_architecture.py --batch          # batch catches up, gap closes
```

See [`docs/how-to/run-lambda-demo.md`](docs/how-to/run-lambda-demo.md) for
a full walkthrough and
[`docs/explanation/architecture.md`](docs/explanation/architecture.md#lambda-architecture-demo)
for the design rationale.

### Data Mesh architecture demo

`examples/run_data_mesh.py` + `src/data_proc/data_mesh/` demonstrate the
**Data Mesh** pattern: two independent domains (customers, orders) each
publish their own data product through a shared, self-serve catalog, and
a consumer discovers and joins both products without either domain
knowing the consumer exists.

```bash
uv run python examples/run_data_mesh.py                 # publish both domains + run the consumer
uv run python examples/run_data_mesh.py --catalog-only   # skip publishing; just browse the catalog
```

See [`docs/how-to/run-data-mesh-demo.md`](docs/how-to/run-data-mesh-demo.md)
for a full walkthrough and
[`docs/explanation/architecture.md`](docs/explanation/architecture.md#data-mesh-architecture-demo)
for the design rationale.

## Quickstart

This project uses [uv](https://docs.astral.sh/uv/) for Python dependency
management.

```bash
# 1. Start PostgreSQL (applies sql/schema.sql automatically)
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
├── data/processed/               Reserved for pipeline/stream output artifacts (gitignored)
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
