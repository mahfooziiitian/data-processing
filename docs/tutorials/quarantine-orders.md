---
diataxis: tutorial
---

# Quarantine invalid orders

Separate a small input fixture into accepted rows and rejected rows with
reasons, then reconcile the counts. The quarantine is an in-memory SQLite
table; it does not change the existing ETL pipeline or write files.

## 1. Inspect the policy

The fixture requires a customer ID and a positive quantity. A source row
number identifies each input even when its business ID is missing or
duplicated. This is a teaching policy, not the full set of rules in
`clean_orders()`.

## 2. Split and reconcile the rows

Run from the repository root:

```bash
uv run python - <<'PY'
import sqlite3

orders = [
    (1, 101, 7, 2),
    (2, 102, None, 1),
    (3, 103, 8, 0),
]
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE accepted (source_row INTEGER, order_id INTEGER, customer_id INTEGER, quantity INTEGER)")
db.execute("CREATE TABLE quarantine (source_row INTEGER, order_id INTEGER, reason TEXT)")
with db:
    for source_row, order_id, customer_id, quantity in orders:
        reasons = []
        if customer_id is None:
            reasons.append("missing customer_id")
        if quantity is None or quantity <= 0:
            reasons.append("quantity must be positive")
        if reasons:
            db.execute("INSERT INTO quarantine VALUES (?, ?, ?)", (source_row, order_id, "; ".join(reasons)))
        else:
            db.execute("INSERT INTO accepted VALUES (?, ?, ?, ?)", (source_row, order_id, customer_id, quantity))

accepted = db.execute("SELECT COUNT(*) FROM accepted").fetchone()[0]
rejected = db.execute("SELECT COUNT(*) FROM quarantine").fetchone()[0]
assert (accepted, rejected) == (1, 2)
assert len(orders) == accepted + rejected
print("Input, accepted, rejected:", len(orders), accepted, rejected)
print("Rejected:", db.execute("SELECT source_row, order_id, reason FROM quarantine ORDER BY source_row").fetchall())
PY
```

## 3. Interpret the result

One row is accepted and two are quarantined. The count equation confirms
that this run classified every fixture row, but does not prove that the
business rules are complete or that customer IDs exist.

The actual ETL drops rows with missing customer IDs and logs the count;
it does not write a quarantine table. A persistent implementation would
also need run/source identifiers, a retry policy, access controls, and a
way to reconcile reprocessed rows without double-counting.
