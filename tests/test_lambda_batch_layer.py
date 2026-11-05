"""Tests for the batch layer: full recompute from CSVs + the event log."""
import pandas as pd

from data_proc.kappa import event_log
from data_proc.lambda_arch import batch_layer


def _write_csvs(tmp_path):
    customers_csv = tmp_path / "customers.csv"
    orders_csv = tmp_path / "orders.csv"
    pd.DataFrame(
        {
            "customer_id": [1, 2],
            "name": ["Alice", "Bob"],
            "email": ["alice@x.com", "bob@x.com"],
            "country": ["USA", "UK"],
        }
    ).to_csv(customers_csv, index=False)
    pd.DataFrame(
        {
            "order_id": [101, 102],
            "customer_id": [1, 1],
            "quantity": [2, 1],
            "unit_price": [5.0, 20.0],
            "order_date": ["2024-01-01", "2024-01-02"],
        }
    ).to_csv(orders_csv, index=False)
    return customers_csv, orders_csv


def test_recompute_batch_view_aggregates_csv_orders_only_when_log_empty(tmp_path):
    customers_csv, orders_csv = _write_csvs(tmp_path)
    log_path = tmp_path / "events.jsonl"

    summary, watermark_offset = batch_layer.recompute_batch_view(
        customers_csv, orders_csv, log_path
    )

    row = summary[summary["customer_id"] == 1].iloc[0]
    assert row["order_count"] == 2
    assert row["total_spent"] == 30.0
    assert watermark_offset == 0


def test_recompute_batch_view_includes_event_sourced_orders(tmp_path):
    customers_csv, orders_csv = _write_csvs(tmp_path)
    log_path = tmp_path / "events.jsonl"
    event_log.append_event(
        log_path,
        {
            "event_type": "order_created", "order_id": 201, "customer_id": 1,
            "quantity": 1, "unit_price": 50.0, "order_date": "2024-02-01",
        },
    )

    summary, watermark_offset = batch_layer.recompute_batch_view(
        customers_csv, orders_csv, log_path
    )

    row = summary[summary["customer_id"] == 1].iloc[0]
    assert row["order_count"] == 3
    assert row["total_spent"] == 80.0
    assert watermark_offset == 1


def test_recompute_batch_view_excludes_cancelled_event_orders(tmp_path):
    customers_csv, orders_csv = _write_csvs(tmp_path)
    log_path = tmp_path / "events.jsonl"
    event_log.append_event(
        log_path,
        {
            "event_type": "order_created", "order_id": 201, "customer_id": 1,
            "quantity": 1, "unit_price": 50.0, "order_date": "2024-02-01",
        },
    )
    event_log.append_event(log_path, {"event_type": "order_cancelled", "order_id": 201})

    summary, _ = batch_layer.recompute_batch_view(customers_csv, orders_csv, log_path)

    row = summary[summary["customer_id"] == 1].iloc[0]
    assert row["order_count"] == 2
    assert row["total_spent"] == 30.0
