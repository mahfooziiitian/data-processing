# Data Engineering Concepts Illustrated

This POC is a teaching vehicle for the following foundational data
engineering concepts. Each links to where it's implemented in the code.

## 1. ETL (Extract, Transform, Load)

The three-stage pattern that structures most batch data pipelines:
pull data from source systems, reshape/clean it, then persist it to a
destination optimized for querying.
→ `src/etl/extract.py`, `src/etl/transform.py`, `src/etl/load.py`

## 2. Data processing patterns: how work gets triggered

ETL describes *what* the pipeline does to data; the processing pattern
describes *when*/*how often* it runs. The three common patterns, in order
of increasing latency requirements and operational complexity:

| Pattern | Trigger | Latency | Example use case |
|---|---|---|---|
| **Batch processing** | Scheduled (hourly/daily) or manually invoked | Minutes–hours | Nightly sales reports, monthly billing |
| **Micro-batching** | Fixed small interval (seconds–minutes) or size threshold | Seconds–minutes | Near-real-time dashboards, periodic fraud scoring |
| **Stream processing** | Continuous, event-by-event as data arrives | Milliseconds–seconds | Live fraud detection, real-time alerting |

This repo implements **batch processing**: `pipeline.run()` reads the full
contents of `data/raw/*.csv` on every invocation and reloads the target
tables from scratch (see "Idempotent loads" below). It is invoked on
demand (`uv run python -m src.etl.pipeline`) or, in production, by a
scheduler (cron, Airflow, Dagster) — the pipeline code itself has no
notion of scheduling.

**Evolving this demo toward the other patterns:**

- **Micro-batching** — keep the same `extract → transform → load`
  structure, but call `pipeline.run()` on a short fixed interval
  (e.g., every 60s) against only the rows that changed since the last run
  (a watermark/cursor on `order_date` or a modified-at column), instead of
  the full CSV each time. This is the natural next step before adopting a
  streaming system, and many "streaming" pipelines in practice are really
  micro-batches under the hood (e.g., Spark Structured Streaming's default
  trigger, or scheduled jobs running every few minutes).
- **Stream processing** — replace `extract_orders_csv()` with a continuous
  event source (e.g., a Kafka consumer or a database change-data-capture
  feed), and replace the batch `transform`/`load` calls with per-event (or
  small-window) handlers. This requires rethinking aggregation: an
  all-at-once `groupby` like `build_customer_order_summary` becomes a
  stateful running aggregate (e.g., windowed counts/sums) maintained
  incrementally as events arrive, since there's no longer a fixed, complete
  input to group over.

The deciding factors when choosing a pattern are: how fresh the output
needs to be, how large/continuous the input volume is, and how much
operational complexity (state management, backpressure, exactly-once
semantics) the team can support. Batch is the simplest to build, test, and
reason about — which is why this demo starts there.

## 3. Multi-source ingestion

Real pipelines rarely read from a single source. This demo combines a
flat-file source (CSV) with an HTTP API source, showing how to normalize
heterogeneous inputs into a common representation (a pandas DataFrame)
before merging them.
→ `extract_customers_csv()` + `extract_customer_enrichment_api()` in
`src/etl/extract.py`

## 4. Data cleaning & validation

Raw data is messy. `clean_customers`/`clean_orders` demonstrate common
cleaning operations: trimming whitespace, normalizing case, parsing dates,
deduplication, and dropping records that fail referential checks (an order
with no `customer_id`).
→ `src/etl/transform.py`

## 5. Derived/computed fields

`line_total = quantity * unit_price` shows how transformation steps compute
new fields rather than merely passing data through — a precursor to more
complex business-rule logic.

## 6. Aggregation / summarization

`build_customer_order_summary` groups fine-grained transactional data
(orders) into a coarser-grained, analytics-friendly table (one row per
customer with lifetime metrics) — the core idea behind building fact and
summary tables in a warehouse.

## 7. Idempotent loads

Using `if_exists="replace"` makes repeated pipeline runs produce the same
end state, a simple way to achieve idempotency for a demo. Production
systems typically use `MERGE`/`UPSERT`, partition overwrites, or slowly
changing dimension (SCD) strategies instead — see "Where to go from here."

## 8. Separation of concerns / testability

Transform functions are pure (no I/O), which makes them trivial to unit
test with small in-memory fixtures (`tests/test_transform.py`) without a
database or network connection. Extract/Load functions isolate I/O so they
can be tested against lightweight substitutes (SQLite instead of Postgres,
a mocked HTTP client instead of a live API).

## 9. Configuration as code

All environment-specific values (DB connection string, API URL, timeouts)
flow through a single `Settings` object (`src/config.py`) sourced from
environment variables — never hardcoded in business logic — so the same
code runs unchanged across local, CI, and production environments.

## Where to go from here

| Concept | How to explore it in this repo |
|---|---|
| Orchestration | Wrap `pipeline.run()` in an Airflow DAG or Dagster job |
| Incremental loads | Replace `if_exists="replace"` with an upsert via `ON CONFLICT` |
| Data quality gates | Add Great Expectations/Pandera checks between transform and load |
| Micro-batching | Add a watermark column and loop `pipeline.run()` on a short interval, processing only new/changed rows (see "Data processing patterns") |
| Streaming | Replace the CSV extractor with a Kafka consumer and stateful windowed aggregation (see "Data processing patterns") |
| Scale | Swap pandas for PySpark DataFrames; the function signatures stay similar |
| Observability | Add structured logging/metrics around each pipeline stage |
