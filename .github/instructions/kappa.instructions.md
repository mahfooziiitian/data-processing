---
applyTo: "src/data_proc/kappa/**/*.py"
---

# Kappa demo library conventions

This package is the reusable **library** half of the Kappa architecture
demo (see the `src/` vs. `examples/` convention in
`.github/copilot-instructions.md`): the single stream-processing path
these modules compose must behave identically whether called for an
ordinary incremental run or a full replay from offset zero. Usage code
(seeding events, CLI wiring, the `process()` entry point) belongs in
`examples/run_kappa_stream.py`, not here.

- `stream_transform.fold_order_events()` must stay a **pure, idempotent
  fold**: it may only depend on the events and prior state it's given, and
  folding the same events twice (or a superset onto empty state) must
  converge on the same result as incrementally folding new events onto
  prior state. This is the property that makes replay correct — don't
  introduce hidden state, randomness, or current-time dependence into it.
- `event_log.py` offsets are 1-based line counts into
  `data/processed/kappa_events.jsonl`; `read_events(log_path, from_offset)`
  must keep returning everything strictly after that offset so a consumer
  can resume exactly where it left off, and `from_offset=0` must replay
  the entire log.
- `checkpoint.py`/`state.py` persist plain JSON — keep event/state payloads
  JSON-serializable (str/int/float/bool/None; no pandas Timestamps or
  other non-JSON types) so round-tripping through these modules doesn't
  silently lose or mutate data.
- If you change the event schema (new fields, new `event_type` values),
  update `stream_transform.py`'s fold logic, `sql/schema.sql`'s
  `kappa_customer_order_summary` table, and
  `examples/run_kappa_stream.py`'s `seed_events()`/`cancel_order()`
  together, and add/adjust a test in `tests/test_kappa_stream_transform.py`
  asserting incremental-vs-replay convergence still holds.
- Persist writes via `data_proc.etl.load.upsert_dataframe()` (key-scoped
  delete+insert), not `load_dataframe(..., if_exists="replace")` — a full
  replace would wipe customers that a given incremental run doesn't touch.
