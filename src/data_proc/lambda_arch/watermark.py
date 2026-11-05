"""Batch watermark: the event-log offset the batch layer has fully covered.

The speed layer only processes events strictly after this offset — its
"gap" window. After each batch run advances the watermark, the speed
layer's prior increments for that now-covered range become redundant,
since the next batch recompute has already absorbed them.
"""
import json
from pathlib import Path


def read_watermark(watermark_path: Path) -> int:
    """Return the last batch-covered offset, or 0 if no batch run yet."""
    if not watermark_path.exists():
        return 0
    return json.loads(watermark_path.read_text(encoding="utf-8"))["offset"]


def write_watermark(watermark_path: Path, offset: int) -> None:
    """Persist the given offset as the new batch watermark."""
    watermark_path.parent.mkdir(parents=True, exist_ok=True)
    watermark_path.write_text(json.dumps({"offset": offset}), encoding="utf-8")
