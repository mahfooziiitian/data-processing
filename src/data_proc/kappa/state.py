"""Durable per-order state: the running result of folding events so far.

Persisting this (instead of re-deriving it from the full log on every
incremental run) is what lets the demo support fast incremental processing
*and* full replay through the exact same fold function — replay is simply
"start from empty state at offset 0" instead of "start from the persisted
state at the last checkpoint".
"""
import json
from pathlib import Path


def read_state(state_path: Path) -> dict[int, dict]:
    """Return the persisted per-order state, or an empty dict if none exists."""
    if not state_path.exists():
        return {}
    raw = json.loads(state_path.read_text(encoding="utf-8"))
    return {int(order_id): event for order_id, event in raw.items()}


def write_state(state_path: Path, order_state: dict[int, dict]) -> None:
    """Persist the per-order state dict, keyed by order_id."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {str(order_id): event for order_id, event in order_state.items()}
    state_path.write_text(json.dumps(payload), encoding="utf-8")


def reset_state(state_path: Path) -> None:
    """Clear persisted state, forcing the next run to rebuild it from
    scratch by folding the entire replayed event log."""
    write_state(state_path, {})
