"""Example: Lambda architecture demo — separate batch and speed layers,
unified at query time by a serving layer.

Unlike `examples/run_kappa_stream.py` (Kappa: one unified stream path that
also handles replay), this script keeps the batch and speed layers as two
independent code paths, faithfully reproducing Lambda's defining
trade-off: the batch layer (`data_proc.lambda_arch.batch_layer`) is slow
but always-correct (it reprocesses the full history from scratch every
run), while the speed layer (`data_proc.lambda_arch.speed_layer`) is fast
but only covers the "gap" since the last batch run. The serving layer
(`data_proc.lambda_arch.serving_layer`) merges both at query time.

This is usage/demo code, not part of the `data_proc` library itself — see
`src/data_proc/lambda_arch/` for the reusable batch/speed/serving/
watermark building blocks this script composes.

Usage:
    uv run python examples/run_lambda_architecture.py --seed-speed 3
        Simulate 3 new orders arriving after the batch dataset, appended
        to the Lambda demo's own event log (data/processed/lambda_events.jsonl).

    uv run python examples/run_lambda_architecture.py
        The usual frequent path: run the (fast) speed layer over events
        since the last batch watermark, then the serving layer merge.

    uv run python examples/run_lambda_architecture.py --batch
        Run the (slow) batch layer: full recompute from the CSVs + ALL
        events seen so far, advancing the watermark past them — then the
        speed+serve path again, now with an empty gap.
"""
import argparse
import logging

import pandas as pd

from data_proc.config import settings
from data_proc.etl.load import get_engine, load_dataframe, read_dataframe, upsert_dataframe
from data_proc.kappa import event_log
from data_proc.lambda_arch import batch_layer, serving_layer, speed_layer, watermark

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_SEED_ORDER_ID_START = 5000


def seed_speed_events(n: int) -> int:
    """Simulate `n` new orders arriving after the batch dataset, appended
    to the Lambda demo's own event log. This is just how the demo
    populates the gap the speed layer is meant to cover — not part of the
    unified-path-style seeding `run_kappa_stream.py` does."""
    customers = pd.read_csv(settings.customers_csv)
    already_seeded = event_log.count_events(settings.lambda_event_log)

    appended = 0
    for i in range(n):
        customer = customers.sample(1, random_state=already_seeded + i).iloc[0]
        event = {
            "event_type": "order_created",
            "order_id": _SEED_ORDER_ID_START + already_seeded + i,
            "customer_id": int(customer["customer_id"]),
            "name": customer["name"],
            "email": customer["email"],
            "country": customer["country"],
            "quantity": 1,
            "unit_price": 15.0,
            "order_date": "2024-07-01",
        }
        event_log.append_event(settings.lambda_event_log, event)
        appended += 1
    logger.info("Seeded %s new order event(s) into the Lambda demo log", appended)
    return appended


def run_batch() -> int:
    """Run the batch layer: full recompute from CSVs + the entire event
    log, then advance the watermark past everything it just covered."""
    batch_df, new_watermark = batch_layer.recompute_batch_view(
        settings.customers_csv, settings.orders_csv, settings.lambda_event_log
    )
    engine = get_engine()
    load_dataframe(batch_df, "lambda_batch_view", engine)
    watermark.write_watermark(settings.lambda_watermark, new_watermark)
    logger.info(
        "Batch layer recomputed %s customer row(s); watermark now %s",
        len(batch_df), new_watermark,
    )
    return new_watermark


def run_speed_and_serve() -> dict:
    """Run the speed layer over events since the watermark, then merge
    the current batch view with that increment via the serving layer."""
    from_offset = watermark.read_watermark(settings.lambda_watermark)
    new_events = event_log.read_events(settings.lambda_event_log, from_offset=from_offset)
    speed_df = speed_layer.compute_speed_increments(new_events)

    engine = get_engine()
    load_dataframe(speed_df, "lambda_speed_view", engine)

    batch_df = read_dataframe("lambda_batch_view", engine)
    served = serving_layer.merge_views(batch_df, speed_df)
    rows_served = upsert_dataframe(served, "lambda_serving_view", "customer_id", engine)

    logger.info(
        "Speed layer processed %s event(s) since watermark %s; "
        "serving layer merged %s row(s)",
        len(new_events), from_offset, rows_served,
    )
    return {"events_processed": len(new_events), "rows_served": rows_served}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seed-speed", type=int, metavar="N", default=0,
        help="simulate N new orders arriving after the batch dataset",
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="run the (slow) batch layer: full recompute, advance the watermark",
    )
    args = parser.parse_args()

    if args.seed_speed:
        seed_speed_events(args.seed_speed)
    if args.batch:
        run_batch()

    run_speed_and_serve()


if __name__ == "__main__":
    main()
