---
diataxis: explanation
---

# Operating and evolving a data pipeline

This page connects the local demos to operational concerns: scheduling,
quality, contract changes, lineage, privacy, and storage choices. The
platform controls discussed below are examples, not features deployed by
this repository.

## Scheduling and observability

The demo scripts run on demand. A scheduler such as cron, Airflow, or
Dagster could invoke them on a cadence and record run status; it is not
configured here. Define how to handle retries and overlapping runs before
scheduling: the file-backed event state and catalog are not a
concurrency-coordination mechanism. A scheduled ETL refresh also replaces
the demo tables' contents, so use an appropriately isolated database.

Track run failures and duration, last successful publication, input and
output counts, rejected counts, source freshness, and event backlog.
Compare offsets only within the same log and account for retention or
reset; offset differences are counts, not time latency. A successful
empty run can hide a stalled source. Alert on missing telemetry as well
as breached thresholds, and select thresholds from an actual freshness
objective. The [monitoring tutorial](../tutorials/monitor-pipeline.md)
demonstrates alerts on simulated values, not live monitoring.

## Quality and contract changes

Cleaning, validation, and reconciliation answer different questions:
cleaning normalizes inputs; validation checks rules; reconciliation
accounts for inputs and outputs. The
[quarantine exercise](../tutorials/quarantine-orders.md) keeps rejection
reasons and checks input = accepted + rejected. In a real system, define
which failures stop publication and which are quarantined, how to retry
them, and whether reconciliation counts rows before or after deduplication.

The mesh validator requires an exact set of declared columns. An added
column therefore fails an old contract even when a consumer could ignore
it. The [contract exercise](../tutorials/evolve-data-contract.md) tests a
new schema and an explicit old-consumer projection. Schema compatibility
alone does not protect against changed meaning, units, nullability, or
freshness. Coordinate producers and consumers, test representative
fixtures, publish a separately named product during a breaking migration,
and retire the old product only after consumers move.

The catalog records the declared freshness SLA and publication timestamp;
the governance check only requires a positive SLA. Neither monitors
freshness or sends alerts.

## Lineage and privacy

For this demo, a simple lineage description is: customer and order CSVs
plus optional API enrichment feed the batch transform, which writes the
customer summary. The mesh consumer instead joins separately published
customer and order products. The catalog records product metadata and a
table location, but it does not capture per-run input versions,
transformations, or column-level lineage. A production lineage record
could associate each output with source identities, input snapshots, code
version, run ID, and owner; protect that metadata as well as the data.

Customer names and email addresses are identity data. Domain separation
and schema checks are not access control. A real deployment should apply
least-privilege database and catalog permissions, secret management,
encryption in transit and at rest, and appropriate retention/deletion
policies. Mask or omit sensitive fields where consumers do not need them;
quarantine and logs can also contain sensitive values. The demo does not
implement these controls.

## Storage formats and layout

| Choice | Benefits | Trade-offs |
| --- | --- | --- |
| CSV | Simple, portable, easy to inspect | Types and nulls need conventions; row-oriented scans often read unnecessary columns |
| Parquet | Columnar reads, typed schema, compression and column pruning | Requires compatible tooling; schema and partition choices still need management |
| PostgreSQL tables | SQL queries, constraints and transactions | Database operations, indexing and capacity require management |

This repository ingests CSV and loads PostgreSQL; it does not implement a
Parquet pipeline. The trade-off depends on the workload: columnar formats are not inherently
faster for every case, so compare data size, query patterns, write frequency,
and tooling.
Partitioning can reduce scans when predicates match partition keys, but
too many small partitions or files can add overhead. File format alone
does not provide transactions, schema evolution, or access control.
