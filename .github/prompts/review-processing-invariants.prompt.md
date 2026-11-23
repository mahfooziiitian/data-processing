---
description: Review processing changes against ETL, Kappa, Lambda, and Data Mesh invariants.
---

# Review processing invariants

Review the specified change, files, or working-tree diff. If no scope is
provided, review the current working-tree changes. Inspect the relevant
implementation, callers, tests, and repository instructions; do not modify
files.

Apply the relevant checks rather than assuming every change affects every
demo:

- **ETL:** transformation purity, fail-soft API enrichment, transactional
  refresh ordering, schema and foreign-key consistency, and repeatability.
- **Kappa:** incremental versus replay convergence, cancellation and stale
  output removal, and checkpoint advancement only over events read.
- **Lambda:** independent batch and speed logic, watermark boundaries,
  supported event types, and consistency of serving results with a fresh
  batch for supported events.
- **Data Mesh:** domain ownership boundaries, schema and governance checks
  before publication, and catalog-based consumer discovery.

Reproduce suspected issues with focused offline tests or temporary,
isolated fixtures where practical. Do not start services, call live APIs,
or modify persistent demo state without permission.

Report actionable findings first, ordered by severity, with file and line
references, impact, triggering conditions, and a recommended fix. Separate
confirmed findings from unverified risks; summarize checks performed and
important coverage gaps. If there are no findings, say so explicitly.
