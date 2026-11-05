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
| --- | --- | --- | --- |
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

## 3. Lambda architecture: combining batch and stream

A common way to get both the throughput/correctness of batch processing
*and* the low latency of streaming is the **Lambda architecture**, which
runs two parallel paths over the same incoming data and merges their
results at query time:

```
                              ┌─────────────┐    ┌──────────────┐
                    ┌────────▶│ Batch layer │───▶│ Batch views  │──┐
                    │         │ (all data,  │    │ (serving     │  │
Incoming data ──────┤         │ recomputed) │    │  layer)      │  ├──▶ Merge ──▶ Query
                    │         └─────────────┘    └──────────────┘  │
                    │         ┌─────────────┐    ┌──────────────┐  │
                    └────────▶│ Speed layer │───▶│ Real-time    │──┘
                              │ (recent     │    │ views        │
                              │  data only) │    │              │
                              └─────────────┘    └──────────────┘
```

- **Batch layer** — processes the *complete* historical dataset on a
  schedule, recomputing exact, authoritative "batch views." This is
  exactly what `src/etl/pipeline.py` does today: it has strong consistency
  but high latency (the view is only as fresh as the last full run).
- **Speed layer** — processes only data arrived *since* the last batch
  run, producing approximate "real-time views" with low latency, to cover
  the gap while the next batch run catches up.
- **Serving layer** — merges the batch view and the real-time view at
  query time (e.g., batch totals for all-but-today plus a speed-layer
  delta for today) so queries always reflect both historical and very
  recent data.

Mapped onto this repo's `customer_order_summary` table: the batch layer is
the current pipeline recomputing full lifetime totals from all orders; a
speed layer would separately aggregate only orders since the last pipeline
run (e.g., from a queue or a `WHERE order_date > :last_run` query) into a
small "delta" table; the serving layer would be a view/query that adds the
batch total and the speed-layer delta together.

The main trade-off is **complexity**: Lambda requires maintaining two
separate codepaths (batch logic and speed logic, often even in different
frameworks/languages — e.g., Spark for batch, Flink/Storm for speed) that
must independently reproduce the same business logic and stay consistent
with each other.

## 4. Kappa architecture: a single stream-processing codebase

**Kappa architecture** is the alternative to Lambda that removes the batch
layer entirely: all data — historical and new — is treated as a single,
replayable stream, processed by one codebase.

```text
All data (historical + new)
        │
        ▼
┌────────────────────┐
│ Immutable log        │  (e.g., Kafka/Pulsar — append-only, retained
│ (append-only events) │   long enough to replay history, not just "new"
└──────────┬──────────┘   events)
           │
           ▼
┌────────────────────────┐
│ Stream processing engine │──▶ Real-time results (normal operation:
│ (e.g., Flink)             │    consume from the current offset)
└──────────┬────────────────┘
           │
           ▼
   Reprocessing for history
   (replay the log from offset 0 through the *same* engine/code when
    logic changes or a bug needs correcting, producing new output
    rather than maintaining a separate batch path)
```

- **Unified codebase** — the same stream-processing logic that produces
  real-time results is also used to recompute historical results, by
  replaying the log from an earlier offset. There is no separate batch
  framework/codebase to keep in sync with the streaming one.
- **Immutable log as system of record** — because the log retains (or can
  reconstruct) full history, "redoing the batch layer" is just "replay the
  stream again," rather than re-running a fundamentally different job.
- **Reprocessing, not two layers** — when transform logic changes (e.g., a
  bug fix to `build_customer_order_summary`'s aggregation), Kappa replays
  the full event history through the corrected stream job to produce
  corrected output, instead of running a parallel batch recompute.

| | Lambda | Kappa |
| --- | --- | --- |
| Codebases | Two (batch + speed), must stay consistent | One (stream only) |
| Historical reprocessing | Re-run the batch layer | Replay the immutable log through the stream engine |
| Typical tooling | Hadoop/Spark (batch) + Storm/Flink (speed) | Kafka/Pulsar (log) + Flink/RisingWave (processing) |
| Operational cost | Higher — two systems to run/debug | Lower — one system, but requires a log durable/long enough to replay |

Kappa isn't a drop-in simplification for every case: it requires the
streaming engine to handle both real-time and bulk-replay workloads well,
and the log retention must cover however far back reprocessing needs to
reach (or history must live in a queryable store the stream job can
rebuild from). Lambda remains a reasonable choice when the batch and
speed logic are genuinely allowed to diverge in accuracy (e.g., an
approximate real-time view is fine as long as the batch view is exact).

## 5. Data mesh: organizational scaling beyond a single pipeline

Lambda and Kappa both answer "how do I process data with the right
latency?" **Data mesh** answers a different question that shows up once an
organization has *many* teams and pipelines: "who owns the data, and how
do independent teams share it without funneling everything through one
central team/platform?"

```
   Domain: Marketing       Domain: Finance         Domain: Sales
  +-------------------+  +-------------------+  +-------------------+
  | owns its own      |  | owns its own      |  | owns its own      |
  | pipeline(s) + DB   |  | pipeline(s) + DB   |  | pipeline(s) + DB   |
  |        |           |  |        |           |  |        |           |
  |        v           |  |        v           |  |        v           |
  |  "data product" <--|--|->"data product" <--|--|->"data product"   |
  | (discoverable,     |  | (discoverable,     |  | (discoverable,     |
  |  documented,       |  |  documented,       |  |  documented,       |
  |  versioned)        |  |  versioned)        |  |  versioned)        |
  +--------+----------+  +--------+----------+  +--------+----------+
           |                      |                      |
           +----------------------+----------------------+
                                  |
                                  v
            Self-serve data platform (shared tooling/infra)
            Federated governance (shared standards: schemas,
            privacy, access control, cataloging) -- not shared data
```

The four pillars of data mesh (Dehghani's formulation):

- **Domain-oriented ownership** — the team closest to a business domain
  (marketing, finance, sales, service...) owns its data end-to-end,
  instead of handing it off to one central data engineering team. In this
  repo's terms: imagine `customers`/`orders` owned and pipelined by a
  "sales" domain team using exactly this `extract.py`/`transform.py`/
  `load.py` structure, rather than one shared team building every
  domain's pipeline.
- **Data as a product** — each domain publishes its output as a
  discoverable, documented, quality-guaranteed "data product" (not just a
  raw table), with a clear owner and schema contract. `customer_order_summary`
  is this repo's one data product; a real mesh would require it to carry
  metadata (owner, freshness SLA, schema version) that other domains can
  depend on without asking the owning team.
- **Self-serve data platform** — a shared platform (infra, orchestration,
  storage, observability tooling) that lets each domain build/operate its
  own pipeline without reinventing infrastructure. `docker-compose.yml`,
  `pyproject.toml`'s dependency groups, and the pytest/MkDocs tooling in
  this repo are the kind of reusable platform primitives a mesh's
  self-serve platform would standardize across domains.
- **Federated computational governance** — global rules (schema
  conventions, data privacy rules, access control, interoperability
  standards) are agreed on centrally and enforced automatically, but
  applied by each domain to its own data — governance is federated, not
  the data itself centralized.

Data mesh is primarily an **organizational/architectural** pattern (who
owns what, how it's shared) rather than a processing-latency pattern like
Lambda/Kappa — a given domain's pipeline can itself be batch, micro-batch,
or streaming. It's a good fit once a single team/pipeline (like this
demo) no longer scales across many independent domains; it's unnecessary
overhead for a project of this repo's size.

## 6. Multi-source ingestion

Real pipelines rarely read from a single source. This demo combines a
flat-file source (CSV) with an HTTP API source, showing how to normalize
heterogeneous inputs into a common representation (a pandas DataFrame)
before merging them.
→ `extract_customers_csv()` + `extract_customer_enrichment_api()` in
`src/etl/extract.py`

## 7. Data cleaning & validation

Raw data is messy. `clean_customers`/`clean_orders` demonstrate common
cleaning operations: trimming whitespace, normalizing case, parsing dates,
deduplication, and dropping records that fail referential checks (an order
with no `customer_id`).
→ `src/etl/transform.py`

## 8. Derived/computed fields

`line_total = quantity * unit_price` shows how transformation steps compute
new fields rather than merely passing data through — a precursor to more
complex business-rule logic.

## 9. Aggregation / summarization

`build_customer_order_summary` groups fine-grained transactional data
(orders) into a coarser-grained, analytics-friendly table (one row per
customer with lifetime metrics) — the core idea behind building fact and
summary tables in a warehouse.

## 10. Idempotent loads

Using `if_exists="replace"` makes repeated pipeline runs produce the same
end state, a simple way to achieve idempotency for a demo. Production
systems typically use `MERGE`/`UPSERT`, partition overwrites, or slowly
changing dimension (SCD) strategies instead — see "Where to go from here."

## 11. Separation of concerns / testability

Transform functions are pure (no I/O), which makes them trivial to unit
test with small in-memory fixtures (`tests/test_transform.py`) without a
database or network connection. Extract/Load functions isolate I/O so they
can be tested against lightweight substitutes (SQLite instead of Postgres,
a mocked HTTP client instead of a live API).

## 12. Configuration as code

All environment-specific values (DB connection string, API URL, timeouts)
flow through a single `Settings` object (`src/config.py`) sourced from
environment variables — never hardcoded in business logic — so the same
code runs unchanged across local, CI, and production environments.

## Where to go from here

| Concept | How to explore it in this repo |
| --- | --- |
| Orchestration | Wrap `pipeline.run()` in an Airflow DAG or Dagster job |
| Incremental loads | Replace `if_exists="replace"` with an upsert via `ON CONFLICT` |
| Data quality gates | Add Great Expectations/Pandera checks between transform and load |
| Micro-batching | Add a watermark column and loop `pipeline.run()` on a short interval, processing only new/changed rows (see "Data processing patterns") |
| Streaming | Replace the CSV extractor with a Kafka consumer and stateful windowed aggregation (see "Data processing patterns") |
| Lambda architecture | Add a speed-layer job computing a delta table since the last batch run, and a merge view combining it with `customer_order_summary` (see "Lambda architecture") |
| Kappa architecture | Replace the CSV extractor with an immutable log (e.g., Kafka), and recompute history by replaying it through the same stream job instead of running a separate batch pipeline (see "Kappa architecture") |
| Data mesh | Treat `customer_order_summary` as a versioned, documented "data product" owned by a domain team, built on shared platform tooling (this repo's `docker-compose.yml`/`pyproject.toml`) rather than a one-off pipeline (see "Data mesh") |
| Scale | Swap pandas for PySpark DataFrames; the function signatures stay similar |
| Observability | Add structured logging/metrics around each pipeline stage |
