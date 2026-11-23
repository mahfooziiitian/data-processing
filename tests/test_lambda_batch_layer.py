"""Tests for the batch layer: full recompute from CSVs + the event log."""
import pandas as pd
import pytest

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


def test_watermark_only_covers_events_read_even_if_log_grows(tmp_path, monkeypatch):
    customers_csv, orders_csv = _write_csvs(tmp_path)
    log_path = tmp_path / "events.jsonl"
    event = {
        "event_type": "order_created", "order_id": 201, "customer_id": 1,
        "quantity": 1, "unit_price": 50.0, "order_date": "2024-02-01",
    }
    read_events = event_log.read_events

    def read_then_append(path, from_offset=0):
        snapshot = read_events(path, from_offset)
        event_log.append_event(path, event)
        return snapshot

    monkeypatch.setattr(event_log, "read_events", read_then_append)
    summary, offset = batch_layer.recompute_batch_view(customers_csv, orders_csv, log_path)

    assert offset == 0
    assert summary.loc[summary["customer_id"] == 1, "order_count"].iloc[0] == 2
    assert len(read_events(log_path, offset)) == 1


def test_batch_rejects_cancellation_of_snapshot_order(tmp_path):
    customers_csv, orders_csv = _write_csvs(tmp_path)
    log_path = tmp_path / "events.jsonl"
    event_log.append_event(log_path, {"event_type": "order_cancelled", "order_id": 101})

    with pytest.raises(ValueError, match="snapshot order"):
        batch_layer.recompute_batch_view(customers_csv, orders_csv, log_path)
