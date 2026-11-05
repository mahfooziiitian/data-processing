---
diataxis: how-to
---

# How to run the Kappa architecture demo

This walks through `examples/run_kappa_stream.py` end-to-end: seeding
events, processing them incrementally, cancelling an order, and replaying
the entire event log from scratch to see Kappa's defining capability in
action. For the conceptual background, see
[Architecture → Kappa architecture demo](../explanation/architecture.md#kappa-architecture-demo).

## Prerequisites

Start PostgreSQL and apply the schema (see
[Setup Guide](../tutorials/setup.md) if you haven't already):

```bash
docker compose up -d --wait
uv sync
```

## 1. Seed the event log

The demo CSVs (`data/raw/customers.csv`, `orders.csv`) are used once to
seed a simulated event-driven order stream — an `order_created` event per
row, appended to `data/processed/kappa_events.jsonl`:

```bash
uv run python examples/run_kappa_stream.py --seed
```

This also runs the stream-processing path once, upserting a per-customer
summary into `kappa_customer_order_summary`:

```bash
docker exec data-processing-demo-postgres \
  psql -U postgres -d data_processing_demo \
  -c "SELECT customer_id, order_count, total_spent FROM kappa_customer_order_summary ORDER BY customer_id;"
```

## 2. Process incrementally

Running the script again with no flags only processes events appended
since the last checkpoint — with nothing new, it's a no-op (0 events
processed, but it still re-upserts current state, confirming the path is
idempotent to re-run):

```bash
uv run python examples/run_kappa_stream.py
```

## 3. Append a cancellation event

Pick an `order_id` from `data/raw/orders.csv` (e.g. `1001`) and cancel it.
This appends a new `order_cancelled` event and immediately processes it,
removing that order from the next customer summary:

```bash
uv run python examples/run_kappa_stream.py --cancel 1001
```

Query again to confirm that customer's `order_count`/`total_spent`
decreased.

## 4. Replay the entire log

Now simulate the scenario Kappa is designed for: a bug fix or logic change
in `src/data_proc/kappa/stream_transform.py` requires re-deriving all
historical results. `--replay` resets the checkpoint and persisted order
state to zero, then reprocesses **every** event in the log — including the
cancellation — through the exact same `process()` function used for
ordinary incremental runs:

```bash
uv run python examples/run_kappa_stream.py --replay
```

Query `kappa_customer_order_summary` once more: the result should be
identical to the state right after step 3, confirming that incremental
processing and full replay converge on the same answer.

## Cleaning up

The event log, checkpoint, and state files are plain local files under
`data/processed/` (gitignored). To start over from an empty log:

```bash
rm -f data/processed/kappa_events.jsonl data/processed/kappa_checkpoint.json data/processed/kappa_order_state.json
```
