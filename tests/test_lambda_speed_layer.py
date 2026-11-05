"""Tests for the speed layer: lightweight aggregation of the events in
the gap since the batch layer's last watermark."""
from data_proc.lambda_arch import speed_layer


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
