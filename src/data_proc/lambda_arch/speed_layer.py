"""Speed layer: the fast, approximate path of a Lambda architecture.

Only processes events appended *after* the batch layer's last watermark —
a small, cheap window — so it can run far more frequently than the batch
layer. Its output is a stopgap: once the next batch run recomputes the
full history (which now includes these same events), the speed layer's
increments for that window become redundant and should be discarded.

Intentionally does NOT share folding logic with `data_proc.kappa.
stream_transform` even though both aggregate order events — that
duplication is the point of this demo: Lambda requires the same business
rule (per-customer order aggregation) to be implemented and kept in sync
twice, once per layer, which is its most commonly cited maintenance cost.
"""
import pandas as pd

_SUMMARY_COLUMNS = [
    "customer_id",
    "name",
    "email",
    "country",
    "order_count",
    "total_spent",
    "last_order_date",
]


def validate_gap_order_ids(events: list[dict], covered_order_ids: set) -> None:
    """Reject creations that reuse IDs from the snapshot or covered log."""
    seen = set(covered_order_ids)
    for event in events:
        if event["event_type"] == "order_created":
            order_id = event["order_id"]
            if order_id in seen:
                raise ValueError(f"Repeated order creation: {order_id}")
            seen.add(order_id)


def compute_speed_increments(events: list[dict]) -> pd.DataFrame:
    """Aggregate only the given (already-gap-filtered) events into a
    per-customer increment: order count, spend, and last order date
    contributed by this window alone — not a full customer summary.

    A cancellation must refer to an order created in this gap: without
    earlier order details this layer cannot subtract a batch-covered order.
    """
    active = {}
    seen = set()
    for event in events:
        order_id = event["order_id"]
        if event["event_type"] == "order_created":
            if order_id in seen:
                raise ValueError(f"Repeated order creation in speed gap: {order_id}")
            seen.add(order_id)
            active[order_id] = event
        elif event["event_type"] == "order_cancelled":
            if order_id not in active:
                raise ValueError(
                    f"Cannot cancel order {order_id}: it was not created in the speed gap"
                )
            del active[order_id]
        else:
            raise ValueError(f"Unsupported order event: {event['event_type']}")
    rows = list(active.values())
    if not rows:
        return pd.DataFrame(columns=_SUMMARY_COLUMNS)

    df = pd.DataFrame(rows)
    df["line_total"] = df["quantity"] * df["unit_price"]

    # keep="last" so the most-recently-seen name/email/country wins if the
    # same customer appears more than once in this window.
    customers = df[["customer_id", "name", "email", "country"]].drop_duplicates(
        subset="customer_id", keep="last"
    )
    summary = (
        df.groupby("customer_id")
        .agg(
            order_count=("order_id", "count"),
            total_spent=("line_total", "sum"),
            last_order_date=("order_date", "max"),
        )
        .reset_index()
    )
    result = customers.merge(summary, on="customer_id", how="left")
    result["total_spent"] = result["total_spent"].round(2)
    return result[_SUMMARY_COLUMNS]
