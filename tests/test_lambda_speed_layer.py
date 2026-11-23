"""Tests for the speed layer: lightweight aggregation of the events in
the gap since the batch layer's last watermark."""
from types import SimpleNamespace

import pandas as pd
import pytest

from data_proc.kappa import event_log
from data_proc.lambda_arch import speed_layer
from data_proc.lambda_arch import watermark
from examples import run_lambda_architecture


def _order_event(order_id, customer_id=1, quantity=1, unit_price=10.0, order_date="2024-07-01"):
    return {
        "event_type": "order_created",
        "order_id": order_id,
        "customer_id": customer_id,
        "name": "Alice",
        "email": "alice@example.com",
        "country": "USA",
        "quantity": quantity,
        "unit_price": unit_price,
        "order_date": order_date,
    }


def test_compute_speed_increments_aggregates_per_customer():
    events = [
        _order_event(order_id=1, quantity=2, unit_price=5.0),
        _order_event(order_id=2, quantity=1, unit_price=20.0, order_date="2024-07-03"),
    ]

    result = speed_layer.compute_speed_increments(events)
    row = result.iloc[0]

    assert row["customer_id"] == 1
    assert row["order_count"] == 2
    assert row["total_spent"] == 30.0
    assert row["last_order_date"] == "2024-07-03"


def test_compute_speed_increments_excludes_cancelled_orders_in_window():
    events = [
        _order_event(order_id=1),
        {"event_type": "order_cancelled", "order_id": 1},
    ]

    result = speed_layer.compute_speed_increments(events)

    assert result.empty


def test_compute_speed_increments_empty_events_returns_empty_frame():
    result = speed_layer.compute_speed_increments([])

    assert result.empty
    assert list(result.columns) == [
        "customer_id", "name", "email", "country",
        "order_count", "total_spent", "last_order_date",
    ]


def test_compute_speed_increments_rejects_cancellation_of_batch_order():
    with pytest.raises(ValueError, match="not created in the speed gap"):
        speed_layer.compute_speed_increments([{"event_type": "order_cancelled", "order_id": 1}])


def test_compute_speed_increments_rejects_repeated_creation():
    with pytest.raises(ValueError, match="Repeated order creation"):
        speed_layer.compute_speed_increments([_order_event(1), _order_event(1)])


@pytest.mark.parametrize("duplicate_source", ["snapshot", "covered_log"])
def test_speed_run_rejects_ids_already_covered_before_writing(tmp_path, monkeypatch, duplicate_source):
    orders_csv = tmp_path / "orders.csv"
    pd.DataFrame({"order_id": [101]}).to_csv(orders_csv, index=False)
    log = tmp_path / "events.jsonl"
    watermark_path = tmp_path / "watermark.json"
    if duplicate_source == "covered_log":
        event_log.append_event(log, _order_event(201))
        watermark.write_watermark(watermark_path, 1)
        duplicate_id = 201
    else:
        duplicate_id = 101
    event_log.append_event(log, _order_event(duplicate_id))
    monkeypatch.setattr(run_lambda_architecture, "settings", SimpleNamespace(
        orders_csv=orders_csv, lambda_event_log=log, lambda_watermark=watermark_path,
    ))
    monkeypatch.setattr(run_lambda_architecture, "get_engine", lambda: pytest.fail("unexpected write"))

    with pytest.raises(ValueError, match="Repeated order creation"):
        run_lambda_architecture.run_speed_and_serve()
