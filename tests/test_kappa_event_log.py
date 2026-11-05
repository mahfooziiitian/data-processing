"""Tests for the append-only event log."""
from data_proc.kappa import event_log


def test_append_event_returns_incrementing_offsets(tmp_path):
    log_path = tmp_path / "events.jsonl"

    first_offset = event_log.append_event(log_path, {"event_type": "order_created", "order_id": 1})
    second_offset = event_log.append_event(log_path, {"event_type": "order_created", "order_id": 2})

    assert first_offset == 1
    assert second_offset == 2


def test_read_events_from_offset_resumes_where_left_off(tmp_path):
    log_path = tmp_path / "events.jsonl"
    for order_id in (1, 2, 3):
        event_log.append_event(log_path, {"event_type": "order_created", "order_id": order_id})

    all_events = event_log.read_events(log_path, from_offset=0)
    tail_events = event_log.read_events(log_path, from_offset=2)

    assert [e["order_id"] for e in all_events] == [1, 2, 3]
    assert [e["order_id"] for e in tail_events] == [3]


def test_read_events_missing_log_returns_empty_list(tmp_path):
    assert event_log.read_events(tmp_path / "missing.jsonl") == []


def test_count_events_missing_log_returns_zero(tmp_path):
    assert event_log.count_events(tmp_path / "missing.jsonl") == 0
