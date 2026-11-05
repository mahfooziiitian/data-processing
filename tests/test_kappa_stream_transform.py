"""Tests for the single stream-processing path: folding events into order
state and aggregating that state into a customer summary.

The key property under test is the one that makes Kappa's replay pattern
correct: incrementally folding events in separate batches onto prior state
must produce the same result as folding the full event history at once.
"""
from data_proc.kappa import stream_transform


def _order_event(order_id, customer_id=1, quantity=1, unit_price=10.0, order_date="2024-01-01"):
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


def test_fold_order_events_keeps_latest_non_cancelled_event_per_order():
    events = [
        _order_event(order_id=1, quantity=1),
        _order_event(order_id=1, quantity=5),  # update: same order_id
    ]

    result = stream_transform.fold_order_events(events)

    assert result[1]["quantity"] == 5


def test_fold_order_events_removes_cancelled_orders():
    events = [
        _order_event(order_id=1),
        {"event_type": "order_cancelled", "order_id": 1},
    ]

    result = stream_transform.fold_order_events(events)

    assert 1 not in result


def test_build_customer_order_summary_aggregates_per_customer():
    order_state = {
        1: _order_event(order_id=1, customer_id=10, quantity=2, unit_price=5.0),
        2: _order_event(order_id=2, customer_id=10, quantity=1, unit_price=20.0, order_date="2024-01-05"),
    }

    summary = stream_transform.build_customer_order_summary(order_state)
    row = summary.iloc[0]

    assert row["customer_id"] == 10
    assert row["order_count"] == 2
    assert row["total_spent"] == 30.0
    assert row["last_order_date"] == "2024-01-05"


def test_build_customer_order_summary_empty_state_returns_empty_frame():
    summary = stream_transform.build_customer_order_summary({})

    assert summary.empty


def test_incremental_folding_matches_full_replay():
    events = [
        _order_event(order_id=1, customer_id=10, quantity=1, unit_price=10.0),
        _order_event(order_id=2, customer_id=10, quantity=2, unit_price=5.0),
        {"event_type": "order_cancelled", "order_id": 1},
    ]

    # Incremental: fold event-by-event, carrying state forward each time.
    incremental_state: dict = {}
    for event in events:
        incremental_state = stream_transform.fold_order_events([event], incremental_state)
    incremental_summary = stream_transform.build_customer_order_summary(incremental_state)

    # Replay: fold the entire history at once from empty state.
    replay_state = stream_transform.fold_order_events(events, {})
    replay_summary = stream_transform.build_customer_order_summary(replay_state)

    assert incremental_summary.equals(replay_summary)
