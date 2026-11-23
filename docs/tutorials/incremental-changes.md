---
diataxis: tutorial
---

# Apply incremental changes and replay them

Apply a simulated change feed to an in-memory SQLite table. We will handle
inserts, updates, deletes, duplicates, and out-of-order versions, then replay
the feed. This is a local exercise, not a CDC connector. Run from the
repository root; it needs only Python's standard library.

## 1. Examine the feed

Each event carries an order ID, a monotonically increasing **per-order**
source version, an operation, and a complete after-image for upserts.
Order 1 is updated, deleted, and then receives an old update. Order 2
receives a duplicate event.

## 2. Apply and replay the events

```bash
uv run python - <<'PY'
import sqlite3

events = [
    (1, 1, "upsert", 10),
    (1, 3, "upsert", 30),
    (1, 2, "upsert", 20),
    (2, 1, "upsert", 15),
    (2, 1, "upsert", 15),
    (1, 4, "delete", None),
    (1, 2, "upsert", 20),
]
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, version INTEGER, amount INTEGER, deleted INTEGER)")

def apply(event):
    order_id, version, operation, amount = event
    if operation not in {"upsert", "delete"}:
        raise ValueError("unknown operation")
    if (operation == "delete") != (amount is None):
        raise ValueError("invalid after-image")
    candidate = (version, amount, int(operation == "delete"))
    current = db.execute(
        "SELECT version, amount, deleted FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if current and version < current[0]:
        return
    if current and version == current[0]:
        if candidate != current:
            raise ValueError("conflicting payload for the same version")
        return
    db.execute(
        "INSERT OR REPLACE INTO orders VALUES (?, ?, ?, ?)",
        (order_id, *candidate),
    )

def snapshot():
    return db.execute("SELECT id, version, amount, deleted FROM orders ORDER BY id").fetchall()

with db:
    for event in events:
        apply(event)
first = snapshot()
with db:
    for event in events:
        apply(event)
assert snapshot() == first == [(1, 4, None, 1), (2, 1, 15, 0)]
try:
    apply((2, 1, "upsert", 99))
except ValueError:
    print("Conflicting current version rejected")
else:
    raise AssertionError("conflicting payload was accepted")
print("State after replay:", snapshot())
print("Active orders:", db.execute("SELECT id, amount FROM orders WHERE deleted = 0").fetchall())
PY
```

## 3. Check the result

The active output is `[(2, 15)]`. Order 1's tombstone retains version 4,
so replaying the old version 2 cannot resurrect it. A duplicate matching
the current version and payload is ignored; a different payload for the
current version raises an error. Older versions are discarded without
checking for conflicts because this example does not retain their payloads.

This exercise assumes trusted, strictly increasing versions per order and
full after-images. A real feed needs a source-consistent snapshot boundary,
durable tombstones and source positions, retention, conflict handling,
and coordinated output and checkpoint commits. It does not read a database
log or implement those guarantees.
