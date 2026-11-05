"""Kappa-architecture building blocks: a single unified stream-processing path.

Unlike the batch ETL package (`data_proc.etl`), which reprocesses bounded
CSV snapshots on each run, this package models the Kappa pattern: an
append-only event log is the source of truth, and *one* processing path
(`stream_transform`) both handles newly appended events and replays the
entire log from offset zero when historical reprocessing is needed (e.g.
after a bug fix or logic change). There is no separate "batch path" and
"speed path" — replay through the same code *is* the batch path.

Modules:
  * `event_log` — append-only JSON-lines log with offset-based reads.
  * `checkpoint` — tracks the last processed offset for incremental runs.
  * `stream_transform` — pure, idempotent folding of events into current
    state (safe to re-run from offset zero without duplicating effects).

This is a library package: reusable building blocks only. The runnable
demo that wires these together lives in `examples/run_kappa_stream.py`.
"""
