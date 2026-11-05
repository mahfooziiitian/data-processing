"""Append-only event log: a minimal stand-in for a Kafka-style topic.

Events are stored as newline-delimited JSON in a single local file. Each
line's 1-based position *is* its offset, so re-reading the file from a
given offset is equivalent to seeking a real log/topic partition. This is
deliberately simple (no partitions, no compaction, no retention policy) —
it exists only to make the single-path replay pattern demonstrable without
a real broker dependency.
"""
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def append_event(log_path: Path, event: dict[str, Any]) -> int:
    """Append one event to the log and return its 1-based offset."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    offset = count_events(log_path)
    logger.debug("Appended event at offset %s: %s", offset, event)
    return offset


def count_events(log_path: Path) -> int:
    """Return the total number of events currently in the log."""
    if not log_path.exists():
        return 0
    with log_path.open("r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def read_events(log_path: Path, from_offset: int = 0) -> list[dict[str, Any]]:
    """Read all events strictly after `from_offset` (0 reads the whole log).

    `from_offset` is a count of already-processed events, so passing the
    last processed offset back in resumes exactly where a consumer left
    off; passing 0 replays the log from the beginning.
    """
    if not log_path.exists():
        return []
    with log_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines[from_offset:]]
