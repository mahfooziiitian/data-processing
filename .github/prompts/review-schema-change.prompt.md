---
description: Review a data shape or database schema change for consistency and migration impact.
---

# Review a schema change

Review the schema change described in the accompanying request or, if
none is specified, the current working-tree changes. Do not modify files.

Trace affected fields and tables through DataFrame producers, loaders,
`sql/schema.sql`, examples, tests, and documentation. Check column names,
types, nullability, keys, foreign keys, and relevant Data Mesh contracts.
Distinguish the batch pipeline's schema-preserving transactional refresh
from independent demo tables loaded with `if_exists="replace"`, which
recreates tables and may discard constraints.

Assess fresh database initialization and existing-volume behavior:
PostgreSQL's initialization scripts run only on first startup. Explain
whether existing data needs a migration or a destructive volume reset;
never reset a volume or start services without permission. Use focused
offline tests where practical, and do not claim SQLite verifies PostgreSQL
behavior.

Report findings in severity order with file and line references, affected
paths, consequences, and concrete recommendations. Include migration and
verification limitations. If no issues are found, say so explicitly.
