"""Example: Kappa architecture demo — a single stream-processing path that
handles both incrementally-arriving events and full historical replay.

Unlike `examples/run_pipeline.py` (Lambda-style: batch-recompute from the
full CSV snapshot every run), this script treats
`data/raw/customers.csv`/`orders.csv` only as a one-time source to *seed*
a simulated event log (`data/processed/kappa_events.jsonl`); from then on,
everything flows through that append-only log via `data_proc.kappa`. The
same `process()` path below handles ordinary incremental runs and full
replays — there is no separate batch path to keep in sync.

This is usage/demo code, not part of the `data_proc` library itself — see
`src/data_proc/kappa/` for the reusable event log, checkpoint, state, and
fold building blocks this script composes.

Usage:
    uv run python examples/run_kappa_stream.py --seed
        Append one order_created event per row of the demo CSVs.

    uv run python examples/run_kappa_stream.py
        Process events appended since the last checkpoint (incremental).

    uv run python examples/run_kappa_stream.py --cancel 1002
        Append a cancellation event for order_id 1002, then process it.

    uv run python examples/run_kappa_stream.py --replay
        Reset the checkpoint and state, then reprocess the ENTIRE log from
        offset 0 through the exact same `process()` path — e.g. after a
        bug fix in `stream_transform`, to re-derive correct historical
        results without a separate backfill mechanism.
"""
import argparse
import logging

import pandas as pd

from data_proc.config import settings
from data_proc.etl.load import get_engine, upsert_dataframe
from data_proc.kappa import checkpoint, event_log
from data_proc.kappa import state as state_store
from data_proc.kappa import stream_transform

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def seed_events() -> int:
    """Append one order_created event per row of the demo CSVs, simulating
    an event-driven order system. This is just how the demo populates the
    log the first time — not part of the unified stream path itself."""
    customers = pd.read_csv(settings.customers_csv)
    orders = pd.read_csv(settings.orders_csv)
    merged = orders.merge(customers, on="customer_id")

    appended = 0
    for _, row in merged.iterrows():
        event = {
            "event_type": "order_created",
            "order_id": int(row["order_id"]),
            "customer_id": int(row["customer_id"]),
            "name": row["name"],
            "email": row["email"],
            "country": row["country"],
            "quantity": int(row["quantity"]),
            "unit_price": float(row["unit_price"]),
            "order_date": str(row["order_date"]),
        }
        event_log.append_event(settings.kappa_event_log, event)
        appended += 1
    logger.info("Seeded %s order_created event(s) into the log", appended)
    return appended


def cancel_order(order_id: int) -> int:
    """Append a cancellation event for an existing order_id."""
    offset = event_log.append_event(
        settings.kappa_event_log,
        {"event_type": "order_cancelled", "order_id": order_id},
    )
    logger.info("Appended order_cancelled event for order_id=%s", order_id)
    return offset


def process() -> dict:
    """The single stream-processing path: fold events since the last
    checkpoint onto the persisted order state, rebuild the customer
    summary, and upsert it. Called identically for an incremental run
    (checkpoint mid-log) or a replay (checkpoint just reset to 0)."""
    from_offset = checkpoint.read_checkpoint(settings.kappa_checkpoint)
    new_events = event_log.read_events(settings.kappa_event_log, from_offset=from_offset)
    current_state = state_store.read_state(settings.kappa_state_path)

    updated_state = stream_transform.fold_order_events(new_events, current_state)
    summary = stream_transform.build_customer_order_summary(updated_state)

    engine = get_engine()
    rows_upserted = upsert_dataframe(
        summary, "kappa_customer_order_summary", "customer_id", engine
    )

    state_store.write_state(settings.kappa_state_path, updated_state)
    new_offset = event_log.count_events(settings.kappa_event_log)
    checkpoint.write_checkpoint(settings.kappa_checkpoint, new_offset)

    logger.info(
        "Processed %s new event(s) (offset %s -> %s); upserted %s customer row(s)",
        len(new_events), from_offset, new_offset, rows_upserted,
    )
    return {"events_processed": len(new_events), "rows_upserted": rows_upserted}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed", action="store_true", help="append sample order events to the log"
    )
    parser.add_argument(
        "--cancel", type=int, metavar="ORDER_ID",
        help="append a cancellation event for ORDER_ID",
    )
    parser.add_argument(
        "--replay", action="store_true",
        help="reset checkpoint/state and reprocess the entire log from offset 0",
    )
    args = parser.parse_args()

    if args.seed:
        seed_events()
    if args.cancel is not None:
        cancel_order(args.cancel)
    if args.replay:
        logger.info("Replaying: resetting checkpoint and state to reprocess the full log")
        checkpoint.reset_checkpoint(settings.kappa_checkpoint)
        state_store.reset_state(settings.kappa_state_path)

    process()


if __name__ == "__main__":
    main()
