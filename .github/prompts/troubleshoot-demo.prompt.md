---
description: Diagnose a repository demo or setup failure without destructive changes.
---

# Troubleshoot a demo

Diagnose the failure described in the accompanying request, including the
demo, command, error, and relevant environment details. If the failure
cannot be identified from the available information, ask for the missing
details. Preserve existing working-tree changes and demo state.

Inspect the relevant example, configuration, walkthrough, and tests.
Check prerequisites and settings such as dependency installation,
`DATA_PROC_HOME`, relative paths, database connectivity and schema
initialization, and optional API enrichment as relevant to the symptom.
Distinguish a database requirement from the ETL API's offline fallback.

Prefer read-only inspection and focused offline tests using mocks, temporary
files, or in-memory SQLite. Do not install dependencies, start services,
call external APIs, modify persistent state, or reset volumes without
permission. In particular, explain that `docker compose --project-directory . -f infra/docker-compose.yml down -v` and
`make clean` remove data before suggesting either.

Report the likely cause with supporting evidence, the least disruptive
resolution, checks performed, and any remaining uncertainty. Do not change
code unless the accompanying request asks for a fix.
