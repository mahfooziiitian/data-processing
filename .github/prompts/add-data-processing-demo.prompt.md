---
description: Implement a focused data-processing demo with tests and documentation.
---

# Add a data-processing demo

Implement the capability described in the accompanying request as a
learning-oriented proof of concept. If the pattern, expected behavior, or
scope is unclear, ask for clarification before choosing an architecture.

1. Inspect the relevant existing demos, repository instructions, tests,
   and documentation. Identify what the new demo teaches, its inputs and
   outputs, and which behaviors are implemented versus illustrative.
2. Put reusable building blocks in `src/data_proc/`, runnable orchestration
   in `examples/`, and any required DDL in `sql/`. Reuse existing helpers
   where appropriate without breaking the intentional separation between
   the Lambda and Kappa implementations.
3. Implement the smallest complete example, including edge-case handling
   and repeatable behavior appropriate to the chosen pattern. Keep existing
   demos and their data independent unless integration was requested.
4. Add focused tests for the new behavior using temporary files, in-memory
   SQLite, and mocked HTTP as needed. Tests must not require Docker,
   PostgreSQL, or a live API.
5. Add or update the relevant walkthrough and architecture explanation.
   Follow the repository's documentation skills and Diátaxis conventions;
   add any new page to `mkdocs.yml` navigation. Update schema and
   configuration examples when affected.

Run the relevant tests and documentation checks. Do not start services,
call live APIs, reset volumes, or overwrite existing demo data without
permission. Explain any unverified integration or limitations in the result.
