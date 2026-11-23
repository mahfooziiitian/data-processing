---
diataxis: tutorial
---

# Monitor simulated scheduled runs

Schedule three short, simulated ticks and evaluate sample run outcomes,
source freshness, and event backlog. This bounded fixture does not run
a real pipeline, contact a service, or send alerts.

## 1. Choose signals

A successful run does not prove that fresh source data arrived. Conversely,
a failed run needs attention even if its previous output is still fresh.
For this exercise, alert when a run fails, source data is over 30 minutes
old, or the log has more than 5 unconsumed events.

## 2. Evaluate three simulated scheduler ticks

Run from the repository root:

```bash
uv run python - <<'PY'
import sched
import time
from datetime import datetime, timedelta, timezone

now = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
runs = [
    ("healthy", "success", now - timedelta(minutes=5), 10, 8),
    ("stale source", "success", now - timedelta(minutes=45), 10, 8),
    ("failed and behind", "failed", now - timedelta(minutes=5), 20, 10),
]

def alerts(status, source_updated, log_end, consumed):
    if not 0 <= consumed <= log_end:
        raise ValueError("offsets must describe the same log snapshot")
    result = []
    if status != "success":
        result.append("run failed")
    if now - source_updated > timedelta(minutes=30):
        result.append("source stale")
    if log_end - consumed > 5:
        result.append("backlog high")
    return result

scheduler = sched.scheduler(time.monotonic, time.sleep)
results = {}

def record(name, status, source_updated, log_end, consumed):
    results[name] = alerts(status, source_updated, log_end, consumed)

for index, (name, status, source_updated, log_end, consumed) in enumerate(runs):
    scheduler.enter(
        index * 0.01, 1, record,
        argument=(name, status, source_updated, log_end, consumed),
    )
scheduler.run()
assert results == {
    "healthy": [],
    "stale source": ["source stale"],
    "failed and behind": ["run failed", "backlog high"],
}
for name, found in results.items():
    print(name, found)
PY
```

## 3. Interpret the alerts

The stale-source run succeeds but still alerts; the failed run also has
a backlog of 10 events. The thresholds are illustrative, not project
defaults. For a real deployment, measure last successful publication too,
distinguish no input from a broken source, alert on missing telemetry, and
use a scheduler and alerting backend. The existing scripts do not collect
or emit these fixture metrics.

See [Operating and evolving pipelines](../explanation/operating-and-evolving.md)
for scheduling and measurement trade-offs.
