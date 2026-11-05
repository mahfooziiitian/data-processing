"""The single stream-processing path: folds order events onto order state.

Events are denormalized (each `order_*` event carries the customer fields
needed downstream) so this module needs no separate "customers" stream or
join — a common simplification for demo event-driven pipelines.

Both functions below are pure. `fold_order_events` folds a list of events
onto an *existing* state dict (empty for a full replay from offset zero,
or the previously-persisted state for an incremental run) and only depends
on `order_id` + `event_type`, so folding the same events twice (replay) or
folding a superset of previously-seen events onto empty state (also
replay) converges on the same result as incrementally folding new events
onto prior state — the fold is idempotent and order-state is a plain
reduction, not a cumulative side effect.
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


def fold_order_events(
    events: list[dict], order_state: dict[int, dict] | None = None
) -> dict[int, dict]:
    """Fold `events` onto `order_state` (or empty state) and return the
    updated per-order state, keyed by `order_id`.

    The latest non-cancelled event for each `order_id` wins; a cancellation
    removes that order from the state entirely.
    """
    state = dict(order_state) if order_state else {}
    for event in events:
        order_id = event["order_id"]
        if event["event_type"] == "order_cancelled":
            state.pop(order_id, None)
            continue
        state[order_id] = event
    return state


def build_customer_order_summary(order_state: dict[int, dict]) -> pd.DataFrame:
    """Aggregate current per-order state into a per-customer summary with
    the same shape as the batch pipeline's `customer_order_summary`,
    computed here via the event-sourced path instead of CSV batch extracts."""
    if not order_state:
        return pd.DataFrame(columns=_SUMMARY_COLUMNS)

    orders = pd.DataFrame(order_state.values())
    orders["line_total"] = orders["quantity"] * orders["unit_price"]

    # keep="last" so each customer's most-recently-seen name/email/country
    # wins, matching the fold's "latest event wins" semantics above.
    customers = orders[["customer_id", "name", "email", "country"]].drop_duplicates(
        subset="customer_id", keep="last"
    )
    summary = (
        orders.groupby("customer_id")
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
