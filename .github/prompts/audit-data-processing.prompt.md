---
description: Audit data-processing concepts, techniques, demos, and infrastructure setup.
---

# Audit the data-processing repository

Review the repository as a learning-oriented data engineering proof of
concept. Audit the current working tree, including uncommitted changes,
and compare implementation with documentation rather than assuming the
intended architecture is implemented. Do not modify repository files.

1. Inventory the implemented processing techniques and architecture demos.
   Compare their code, tests, and documentation for conceptual accuracy,
   consistent terminology, and clearly stated limitations. Distinguish
   implemented behavior from hypothetical production designs.
2. Trace the data flow from inputs through transformation and storage.
   Check correctness, data quality, error handling, repeatability, and
   whether the demonstrations actually illustrate their stated concepts.
   Examine the ETL, Kappa, Lambda, and Data Mesh invariants documented in
   the repository instructions. Check transaction and foreign-key behavior,
   replay and removal of stale results, checkpoint/watermark boundaries,
   supported event types, and domain contract and ownership boundaries.
3. Review the proof of concept and demos for runnable examples, meaningful
   sample data, expected outputs, test coverage of important behavior, and
   consistency between scripts and walkthroughs.
4. Review local infrastructure and setup: dependencies, configuration,
   Docker Compose, database schema initialization, setup commands, and
   teardown or reset guidance. Identify prerequisites, destructive reset
   steps, and failure modes that could prevent a new user from reproducing
   a demo.
5. Identify missing or misleading explanations and notable gaps in
   techniques or examples, prioritizing those relevant to the repository's
   stated learning goals. Avoid treating production-grade infrastructure
   as mandatory for a small demo; explain trade-offs instead.

Inspect the relevant source, configuration, tests, and documentation.
Run focused, non-destructive checks when practical, using temporary files,
mocked HTTP, and in-memory SQLite rather than existing demo state. For
example, the offline unit suite can be run with
`PYTHONDONTWRITEBYTECODE=1 uv run --offline --no-sync pytest -q -p no:cacheprovider`.
Do not install dependencies, start services, reset volumes, modify persistent
data, or invoke external APIs without permission. SQLite does not prove
PostgreSQL behavior; distinguish code-based conclusions from reproduced
results and report checks you could not run.

## Report

List actionable findings first, ordered by severity. For each, include its
impact, evidence with file paths and line numbers, reproduction or relevant
conditions, and a specific recommendation. Separate correctness and
reproducibility issues from optional learning enhancements. Summarize the
areas reviewed, checks performed, and important limitations. If there are
no findings, say so explicitly.
