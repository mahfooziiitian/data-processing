"""Tests for checkpoint and order-state persistence."""
from data_proc.kappa import checkpoint, state


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
