"""Tests for the serving layer: merging the batch view with the speed
layer's increments into one queryable result.

Also verifies Lambda's core consistency property: serving(batch, speed)
for a gap should match what the batch layer would compute if it
recomputed with that same gap's events already included — i.e. the speed
layer's contribution is eventually absorbed losslessly once batch catches
up.
"""
import pandas as pd

from data_proc.kappa import event_log
from data_proc.lambda_arch import batch_layer, serving_layer, speed_layer


def _batch_row(customer_id=1, name="Alice", email="alice@example.com", country="USA",
                order_count=2, total_spent=30.0, last_order_date="2024-01-02"):
    return pd.DataFrame([{
        "customer_id": customer_id, "name": name, "email": email, "country": country,
        "order_count": order_count, "total_spent": total_spent,
        "last_order_date": last_order_date,
    }])


def _speed_row(customer_id=1, name="Alice", email="alice@example.com", country="USA",
               order_count=1, total_spent=50.0, last_order_date="2024-02-01"):
    return pd.DataFrame([{
        "customer_id": customer_id, "name": name, "email": email, "country": country,
        "order_count": order_count, "total_spent": total_spent,
        "last_order_date": last_order_date,
    }])


def test_merge_views_sums_counts_and_spend_for_existing_customer():
    merged = serving_layer.merge_views(_batch_row(), _speed_row())
    row = merged.iloc[0]

    assert row["order_count"] == 3
    assert row["total_spent"] == 80.0
    assert row["last_order_date"] == "2024-02-01"


def test_merge_views_includes_customer_only_present_in_speed_layer():
    batch_df = _batch_row(customer_id=1)
    speed_df = _speed_row(customer_id=2, name="Bob", email="bob@example.com", country="UK")

    merged = serving_layer.merge_views(batch_df, speed_df)

    assert set(merged["customer_id"]) == {1, 2}


def test_merge_views_empty_speed_returns_batch_unchanged():
    batch_df = _batch_row()

    merged = serving_layer.merge_views(batch_df, pd.DataFrame())

    assert merged.iloc[0]["order_count"] == 2


def test_merge_views_empty_batch_returns_speed_unchanged():
    speed_df = _speed_row()

    merged = serving_layer.merge_views(pd.DataFrame(), speed_df)

    assert merged.iloc[0]["order_count"] == 1


def test_serving_result_matches_batch_layer_once_batch_absorbs_the_gap(tmp_path):
    """The key Lambda consistency property: merging an old batch view with
    speed-layer increments for the gap must equal what a fresh batch
    recompute (including that gap's events) would produce."""
    customers_csv = tmp_path / "customers.csv"
    orders_csv = tmp_path / "orders.csv"
    pd.DataFrame({
        "customer_id": [1], "name": ["Alice"], "email": ["alice@x.com"], "country": ["USA"],
    }).to_csv(customers_csv, index=False)
    pd.DataFrame({
        "order_id": [101], "customer_id": [1], "quantity": [2], "unit_price": [5.0],
        "order_date": ["2024-01-01"],
    }).to_csv(orders_csv, index=False)
    log_path = tmp_path / "events.jsonl"

    # Batch layer runs first, before the gap event exists.
    old_batch_df, old_watermark = batch_layer.recompute_batch_view(
        customers_csv, orders_csv, log_path
    )

    # A new order arrives after that batch run (the "gap").
    gap_event = {
        "event_type": "order_created", "order_id": 201, "customer_id": 1,
        "name": "Alice", "email": "alice@x.com", "country": "USA",
        "quantity": 1, "unit_price": 50.0, "order_date": "2024-02-01",
    }
    event_log.append_event(log_path, gap_event)

    # Speed layer covers just the gap; serving layer merges it with the
    # (stale) batch view.
    gap_events = event_log.read_events(log_path, from_offset=old_watermark)
    speed_df = speed_layer.compute_speed_increments(gap_events)
    served = serving_layer.merge_views(old_batch_df, speed_df)

    # A fresh batch recompute now includes the gap event directly.
    new_batch_df, _ = batch_layer.recompute_batch_view(customers_csv, orders_csv, log_path)

    served_row = served[served["customer_id"] == 1].iloc[0]
    new_batch_row = new_batch_df[new_batch_df["customer_id"] == 1].iloc[0]
    assert served_row["order_count"] == new_batch_row["order_count"]
    assert served_row["total_spent"] == new_batch_row["total_spent"]
