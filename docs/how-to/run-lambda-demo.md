---
diataxis: how-to
---

# How to run the Lambda architecture demo

This walks through `examples/run_lambda_architecture.py` end-to-end: an
initial batch run, simulating new orders arriving in the "gap" since that
batch run, serving a merged view, and then running batch again to watch
the gap close. For the conceptual background, see
[Architecture → Lambda architecture demo](../explanation/architecture.md#lambda-architecture-demo).

## Prerequisites

Start PostgreSQL and apply the schema (see
[Setup Guide](../tutorials/setup.md) if you haven't already):

```bash
docker compose up -d --wait
uv sync
```

## 1. Run the batch layer

The batch layer does a full, slow recompute from `data/raw/customers.csv`
+ `orders.csv` (plus any events already in the Lambda demo's log — none
yet), writing `lambda_batch_view` and advancing the watermark:

```bash
uv run python examples/run_lambda_architecture.py --batch
```

```bash
docker exec data-processing-demo-postgres \
  psql -U postgres -d data_processing_demo \
  -c "SELECT customer_id, order_count, total_spent FROM lambda_serving_view ORDER BY customer_id;"
```

With no gap events yet, `lambda_serving_view` exactly matches
`lambda_batch_view`.

## 2. Simulate new orders arriving (the "gap")

Seed a few simulated orders into the Lambda demo's own event log
(`data/processed/lambda_events.jsonl`) — these represent orders that
arrived *after* the batch run above, which the batch layer hasn't seen:

```bash
uv run python examples/run_lambda_architecture.py --seed-speed 3
```

This also runs the speed layer (covering just those 3 new events) and the
serving layer merge. Query again:

```bash
docker exec data-processing-demo-postgres \
  psql -U postgres -d data_processing_demo \
  -c "SELECT customer_id, order_count, total_spent FROM lambda_serving_view ORDER BY customer_id;"
```

Some customers' `order_count`/`total_spent` should now be higher than in
step 1 — the speed layer's increments are flowing through. Compare against
`lambda_batch_view`, which is **unchanged** (still stale, as expected —
the batch layer hasn't run again):

```bash
docker exec data-processing-demo-postgres \
  psql -U postgres -d data_processing_demo \
  -c "SELECT customer_id, order_count, total_spent FROM lambda_batch_view ORDER BY customer_id;"
```

## 3. Run the batch layer again to close the gap

```bash
uv run python examples/run_lambda_architecture.py --batch
```

This recomputes `lambda_batch_view` from the CSVs *plus all 3 gap
events*, and advances the watermark past them. Query `lambda_batch_view`
again: it should now match the serving-view numbers from step 2 exactly —
the batch layer has caught up and fully absorbed what the speed layer was
covering. The speed layer's next run will find no new events (an empty
gap) until more orders arrive.

## Cleaning up

The event log and watermark are plain local files under
`data/processed/` (gitignored). To start over from an empty log:

```bash
rm -f data/processed/lambda_events.jsonl data/processed/lambda_watermark.json
```
