"""Batch layer: the authoritative, slow path of a Lambda architecture.

Recomputes per-customer order aggregates from the FULL historical dataset
(the original CSV orders *plus* every event appended to the event log so
far) every time it runs. This is deliberately a full, stateless recompute
— the batch layer is allowed to be slow precisely because it always
starts from scratch, which is what makes it simple to reason about and
always eventually correct, even if a bug in the speed layer produced
wrong intermediate results.
"""
from pathlib import Path

import pandas as pd

from data_proc.kappa import event_log

_SUMMARY_COLUMNS = [
    "customer_id",
    "name",
    "email",
    "country",
    "order_count",
    "total_spent",
    "last_order_date",
]


def _events_to_orders_frame(events: list[dict]) -> pd.DataFrame:
    """Reduce event-sourced order_created/order_cancelled events to the
    current set of non-cancelled orders, shaped like the CSV orders."""
    cancelled_ids = {e["order_id"] for e in events if e["event_type"] == "order_cancelled"}
    rows = [
        e for e in events
        if e["event_type"] == "order_created" and e["order_id"] not in cancelled_ids
    ]
    if not rows:
        return pd.DataFrame(
            columns=["order_id", "customer_id", "quantity", "unit_price", "order_date"]
        )
    return pd.DataFrame(rows)[["order_id", "customer_id", "quantity", "unit_price", "order_date"]]


def recompute_batch_view(
    customers_csv: Path, orders_csv: Path, event_log_path: Path
) -> tuple[pd.DataFrame, int]:
    """Full recompute of the per-customer order summary from the CSV
    snapshot plus every event in the log (from offset 0).

    Returns `(summary_df, watermark_offset)`: the recomputed view and the
    event-log offset it fully covers, for the caller to persist as the
    new batch watermark so the speed layer knows its gap now starts here.
    """
    customers = pd.read_csv(customers_csv)
    orders = pd.read_csv(orders_csv)[
        ["order_id", "customer_id", "quantity", "unit_price", "order_date"]
    ]

    all_events = event_log.read_events(event_log_path, from_offset=0)
    event_orders = _events_to_orders_frame(all_events)
    combined_orders = pd.concat([orders, event_orders], ignore_index=True)
    combined_orders["line_total"] = combined_orders["quantity"] * combined_orders["unit_price"]

    summary = (
        combined_orders.groupby("customer_id")
        .agg(
            order_count=("order_id", "count"),
            total_spent=("line_total", "sum"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    result = customers.merge(summary, on="customer_id", how="left")
    result["order_count"] = result["order_count"].fillna(0).astype(int)
    result["total_spent"] = result["total_spent"].fillna(0.0).round(2)

    watermark_offset = event_log.count_events(event_log_path)
    return result[_SUMMARY_COLUMNS], watermark_offset
