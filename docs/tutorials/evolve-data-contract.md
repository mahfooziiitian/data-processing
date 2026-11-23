---
diataxis: tutorial
---

# Evolve a data contract

Use the demo's actual schema validator to see why adding a producer column
breaks an exact-column contract, then validate a versioned product and an
old consumer projection. The exercise uses in-memory DataFrames and writes
no product or catalog files.

## 1. Define the original contract and consumer

The original consumer expects exactly `customer_id` and `name`. A new
producer adds `country`. The demo rejects undeclared columns, even when
the old consumer would not use them.

## 2. Compare the producer and consumer schemas

Run from the repository root with project dependencies installed:

```bash
uv run python - <<'PY'
from dataclasses import replace

import pandas as pd
from data_proc.data_mesh.contract import DataContract, validate_schema

v1 = DataContract(
    domain="customers", name="profile", version="v1",
    owner="customers-team", description="Customer profile product.",
    schema={"customer_id": "int", "name": "string"},
)
v2 = replace(v1, name="profile_v2", version="v2",
             schema={**v1.schema, "country": "string"})
producer_v2 = pd.DataFrame({"customer_id": [1], "name": ["Ada"], "country": ["GB"]})

old_contract_errors = validate_schema(producer_v2, v1)
assert old_contract_errors == ["undeclared column 'country' not in contract schema"]
assert validate_schema(producer_v2, v2) == []

old_consumer_input = producer_v2[list(v1.schema)]
assert validate_schema(old_consumer_input, v1) == []
assert old_consumer_input.to_dict("records") == [{"customer_id": 1, "name": "Ada"}]
print("Old contract:", old_contract_errors)
print("Projected old consumer:", old_consumer_input.to_dict("records"))
PY
```

## 3. Plan the migration

The v2 producer matches its own contract. The explicit projection gives
this particular v1 consumer its expected columns; it does not prove that
all consumers are compatible. Test representative consumer behavior and
semantic changes as well as schema shape.

The catalog stores one entry per product name, so publishing a separate
name can support a transition while consumers migrate. Coordinate
publication and eventual retirement; this exercise does not publish or
automatically provide a compatibility view. The contract records a
freshness SLA, but the demo only validates that its value is positive:
it does not monitor the SLA.
