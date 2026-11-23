---
diataxis: tutorial
---

# Aggregate out-of-order events into time windows

Compute revenue in five-minute UTC windows and verify what happens when
an event arrives after its window closes. Run from the repository root
with `uv`. The exercise uses Python's standard library and an inline
fixture.

## 1. Read the events in arrival order

D arrives out of order but can still contribute to the first window.
Predict what happens to F, which has the same timestamp.

| Arrival | Event time (UTC) | Revenue |
| --- | --- | ---: |
| A | 12:01 | 10 |
| B | 12:04 | 20 |
| C | 12:06 | 7 |
| D | 12:03 | 5 |
| E | 12:09 | 4 |
| F | 12:03 | 99 |

Before each event, the watermark equals the largest event time seen so far minus two minutes. This
exercise closes a window when its end is at or before that watermark.
Windows include their start and exclude their end.

## 2. Run the aggregation

```bash
uv run python - <<'PY'
from collections import defaultdict
from datetime import datetime, timedelta

events = [
    ("A", "12:01", 10),
    ("B", "12:04", 20),
    ("C", "12:06", 7),
    ("D", "12:03", 5),
    ("E", "12:09", 4),
    ("F", "12:03", 99),
]
width = timedelta(minutes=5)
delay = timedelta(minutes=2)
latest = None
totals = defaultdict(int)
rejected = []

for event_id, clock_time, amount in events:
    timestamp = datetime.fromisoformat(f"2026-01-01T{clock_time}:00+00:00")
    start = timestamp.replace(minute=timestamp.minute // 5 * 5)
    watermark = latest - delay if latest is not None else None
    if watermark is not None and start + width <= watermark:
        rejected.append(event_id)
        continue
    totals[start] += amount
    latest = timestamp if latest is None else max(latest, timestamp)

result = {start.strftime("%H:%M"): totals[start] for start in sorted(totals)}
print(result)
print("Rejected:", rejected)
assert result == {"12:00": 35, "12:05": 11}
assert rejected == ["F"]
PY
```

## 3. Check which arrivals made it into each window

D arrives when the watermark is 12:04, so the window ending at 12:05
still accepts it. E moves the watermark to 12:07. F arrives next and is
rejected because its window has closed. The final print includes the
12:05 window as a snapshot of its current total.

Here the watermark measures progress in event time. The [Lambda
demo](../how-to/run-lambda-demo.md) uses a log offset to count events
already covered by the batch view. An offset cannot tell you whether a
newly appended event occurred before an event-time window closed.
