"""Tests for checkpoint and order-state persistence."""
from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine, text

from data_proc.kappa import checkpoint, event_log, state
from examples import run_kappa_stream


def test_read_checkpoint_missing_file_returns_zero(tmp_path):
    assert checkpoint.read_checkpoint(tmp_path / "missing.json") == 0


def test_write_then_read_checkpoint_roundtrips(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.json"

    checkpoint.write_checkpoint(checkpoint_path, 42)

    assert checkpoint.read_checkpoint(checkpoint_path) == 42


def test_reset_checkpoint_sets_offset_to_zero(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.json"
    checkpoint.write_checkpoint(checkpoint_path, 42)

    checkpoint.reset_checkpoint(checkpoint_path)

    assert checkpoint.read_checkpoint(checkpoint_path) == 0


def test_read_state_missing_file_returns_empty_dict(tmp_path):
    assert state.read_state(tmp_path / "missing.json") == {}


def test_write_then_read_state_roundtrips_with_int_keys(tmp_path):
    state_path = tmp_path / "state.json"
    order_state = {1: {"event_type": "order_created", "order_id": 1}}

    state.write_state(state_path, order_state)

    assert state.read_state(state_path) == order_state


def test_reset_state_clears_persisted_state(tmp_path):
    state_path = tmp_path / "state.json"
    state.write_state(state_path, {1: {"event_type": "order_created", "order_id": 1}})

    state.reset_state(state_path)

    assert state.read_state(state_path) == {}


def _setup_process(tmp_path, monkeypatch):
    settings = SimpleNamespace(
        kappa_event_log=tmp_path / "events.jsonl",
        kappa_checkpoint=tmp_path / "checkpoint.json",
        kappa_state_path=tmp_path / "state.json",
    )
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE kappa_customer_order_summary ("
            "customer_id INTEGER PRIMARY KEY, name TEXT, email TEXT, country TEXT, "
            "order_count INTEGER, total_spent REAL, last_order_date TEXT)"
        ))
    monkeypatch.setattr(run_kappa_stream, "settings", settings)
    monkeypatch.setattr(run_kappa_stream, "get_engine", lambda: engine)
    return settings, engine


def _order(order_id, customer_id):
    return {
        "event_type": "order_created", "order_id": order_id, "customer_id": customer_id,
        "name": "Alice", "email": "alice@example.com", "country": "USA",
        "quantity": 1, "unit_price": 10.0, "order_date": "2024-01-01",
    }


def test_process_removes_cancelled_customer_and_replay_stale_rows(tmp_path, monkeypatch):
    settings, engine = _setup_process(tmp_path, monkeypatch)
    event_log.append_event(settings.kappa_event_log, _order(1, 1))
    event_log.append_event(settings.kappa_event_log, _order(2, 2))
    run_kappa_stream.process()
    event_log.append_event(settings.kappa_event_log, {"event_type": "order_cancelled", "order_id": 1})
    run_kappa_stream.process()

    with engine.connect() as conn:
        assert conn.execute(text("SELECT customer_id FROM kappa_customer_order_summary")).scalars().all() == [2]
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO kappa_customer_order_summary (customer_id) VALUES (1)"))
    checkpoint.reset_checkpoint(settings.kappa_checkpoint)
    state.reset_state(settings.kappa_state_path)
    run_kappa_stream.process()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT customer_id FROM kappa_customer_order_summary")).scalars().all() == [2]

    event_log.append_event(settings.kappa_event_log, {"event_type": "order_cancelled", "order_id": 2})
    run_kappa_stream.process()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT COUNT(*) FROM kappa_customer_order_summary")).scalar() == 0


def test_process_checkpoints_only_the_read_snapshot(tmp_path, monkeypatch):
    settings, engine = _setup_process(tmp_path, monkeypatch)
    event_log.append_event(settings.kappa_event_log, _order(1, 1))
    read_events = event_log.read_events

    def read_then_append(path, from_offset=0):
        snapshot = read_events(path, from_offset)
        event_log.append_event(path, _order(2, 2))
        return snapshot

    monkeypatch.setattr(event_log, "read_events", read_then_append)
    run_kappa_stream.process()
    assert checkpoint.read_checkpoint(settings.kappa_checkpoint) == 1
    monkeypatch.setattr(event_log, "read_events", read_events)
    run_kappa_stream.process()
    with engine.connect() as conn:
        assert conn.execute(text("SELECT customer_id FROM kappa_customer_order_summary ORDER BY customer_id")).scalars().all() == [1, 2]


def test_retry_after_checkpoint_write_failure_keeps_summary(tmp_path, monkeypatch):
    settings, engine = _setup_process(tmp_path, monkeypatch)
    event_log.append_event(settings.kappa_event_log, _order(1, 1))
    query = text(
        "SELECT customer_id, order_count, total_spent "
        "FROM kappa_customer_order_summary"
    )

    def fail_checkpoint_write(path, offset):
        raise OSError("simulated checkpoint write failure")

    with monkeypatch.context() as patch:
        patch.setattr(checkpoint, "write_checkpoint", fail_checkpoint_write)
        with pytest.raises(OSError, match="simulated checkpoint write failure"):
            run_kappa_stream.process()

    assert checkpoint.read_checkpoint(settings.kappa_checkpoint) == 0
    assert set(state.read_state(settings.kappa_state_path)) == {1}
    with engine.connect() as conn:
        assert conn.execute(query).all() == [(1, 1, 10.0)]

    result = run_kappa_stream.process()

    assert result["events_processed"] == 1
    assert checkpoint.read_checkpoint(settings.kappa_checkpoint) == 1
    with engine.connect() as conn:
        assert conn.execute(query).all() == [(1, 1, 10.0)]
