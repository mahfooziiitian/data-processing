---
diataxis: reference
---

# Demo commands and state

Commands run from the repository root. The demos use the PostgreSQL
database configured by `DATABASE_URL`. The default CSV inputs are
`data/raw/customers.csv` and `data/raw/orders.csv`.

| Demo | Entry point | Inputs | Output tables |
| --- | --- | --- | --- |
| [Batch ETL](../tutorials/setup.md) | `uv run python examples/run_pipeline.py` | Customer and order CSVs, optional REST enrichment | `customers`, `orders`, `customer_order_summary` |
| [Kappa](../how-to/run-kappa-demo.md) | `uv run python examples/run_kappa_stream.py` | Event log, checkpoint, saved order state. Seeding reads both CSVs. | `kappa_customer_order_summary` |
| [Lambda](../how-to/run-lambda-demo.md) | `uv run python examples/run_lambda_architecture.py` | Customer and order CSVs, separate event log, batch coverage offset | `lambda_batch_view`, `lambda_speed_view`, `lambda_serving_view` |
| [Data Mesh](../how-to/run-data-mesh-demo.md) | `uv run python examples/run_data_mesh.py` | Customer and order CSVs, optional REST enrichment for the customer product. The consumer uses the catalog and product tables. | `data_mesh_customers_product`, `data_mesh_orders_product`, `data_mesh_consumer_view` |

## Command options

| Demo | Option | Effect |
| --- | --- | --- |
| Kappa | No flags | Fold events after the checkpoint, refresh the summary, and save state and checkpoint. |
| Kappa | `--seed` | Append sample order events and process the log. Repeated seeding appends additional log entries. |
| Kappa | `--cancel ORDER_ID` | Append a cancellation and process the log. |
| Kappa | `--replay` | Reset saved order state and checkpoint, then rebuild the summary from the retained log. |
| Lambda | No flags | Read the existing batch view and merge it with the speed-layer result. Run with `--batch` for the initial populated batch view. |
| Lambda | `--batch` | Recompute the batch view and update its coverage offset before running speed and serving. |
| Lambda | `--seed-speed N` | Append simulated events before running the requested layers. |
| Data Mesh | No flags | Publish both products, print the catalog, and refresh the consumer table. |
| Data Mesh | `--catalog-only` | Skip publishing, print the catalog, and still refresh the consumer table. Requires both products to be published. |

## Persisted files

Paths below are relative to `DATA_PROC_HOME`, which defaults to the
working directory. Each override accepts an absolute path or a path
relative to that home.

| Default path | Environment override | Contents or reset behavior |
| --- | --- | --- |
| `data/raw/customers.csv` | `CUSTOMERS_CSV` | Customer source records |
| `data/raw/orders.csv` | `ORDERS_CSV` | Order source records |
| `data/processed/kappa_events.jsonl` | `KAPPA_EVENT_LOG` | Event history retained by `--replay`. Deleting this file discards the history. |
| `data/processed/kappa_checkpoint.json` | `KAPPA_CHECKPOINT` | Consumed event count. `--replay` resets it to zero before processing. |
| `data/processed/kappa_order_state.json` | `KAPPA_STATE_PATH` | Saved order state. `--replay` clears and rebuilds it. |
| `data/processed/lambda_events.jsonl` | `LAMBDA_EVENT_LOG` | Events used by both Lambda layers. Deleting this file discards the history. |
| `data/processed/lambda_watermark.json` | `LAMBDA_WATERMARK` | Number of events included in the batch view. `--batch` regenerates it with the view. |
| `data/processed/data_mesh_catalog.json` | `DATA_MESH_CATALOG` | Product metadata and table locations. Publishing registers both products again. |

File deletion leaves existing database tables in place. Keep the Lambda
batch view and its coverage offset together. If either is missing or
stale after an interruption, rebuild both with `--batch` using the retained
inputs.
