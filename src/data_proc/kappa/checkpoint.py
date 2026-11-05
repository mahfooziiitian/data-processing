"""Checkpoint tracking: remembers the last offset a consumer has processed.

This is what lets the single stream-processing path support two modes with
no code change: an incremental run reads the checkpoint and only processes
events appended since then, while a replay resets the checkpoint to zero
first so the *same* processing function re-derives state from the entire
log from scratch.
"""
import json
from pathlib import Path


def read_checkpoint(checkpoint_path: Path) -> int:
    """Return the last processed offset, or 0 if no checkpoint exists yet."""
    if not checkpoint_path.exists():
        return 0
    return json.loads(checkpoint_path.read_text(encoding="utf-8"))["offset"]


def write_checkpoint(checkpoint_path: Path, offset: int) -> None:
    """Persist the given offset as the new last-processed checkpoint."""
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(json.dumps({"offset": offset}), encoding="utf-8")


def reset_checkpoint(checkpoint_path: Path) -> None:
    """Reset the checkpoint to offset 0, forcing the next run to replay
    the entire event log through the same processing path."""
    write_checkpoint(checkpoint_path, 0)
