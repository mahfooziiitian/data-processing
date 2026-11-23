---
description: Audit data quality and validation in a selected data-processing flow.
---

# Audit data quality

Review the flow or data source named in the accompanying request. If none
is specified, examine the batch ETL flow and describe that scope. Inspect
source data, extraction, transforms, persistence, tests, and documentation;
do not modify files.

Trace the handling of missing and invalid values, duplicates, identifiers
and references, dates, numeric values and aggregates, schema contracts,
and optional API enrichment. Consider how failures or dropped records
affect the outputs and whether the documented behavior matches the code.
Focus on issues relevant to the demo's stated purpose; distinguish an
actual correctness defect from a production-oriented enhancement.

Use small in-memory fixtures, mocked HTTP, and temporary files to reproduce
suspected issues when practical. Do not call live APIs, start services, or
modify persistent data without permission.

Report actionable findings in severity order with file and line references,
example input or triggering conditions, observed or expected impact, and
a specific recommendation. Note unverified concerns, tests performed, and
important coverage gaps. If there are no findings, say so explicitly.
