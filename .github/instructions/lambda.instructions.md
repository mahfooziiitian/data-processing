---
applyTo: "src/data_proc/lambda_arch/**/*.py"
---

# Lambda demo library conventions

This package is the reusable **library** half of the Lambda architecture
demo (see the `src/` vs. `examples/` convention in
`.github/copilot-instructions.md`): it deliberately keeps the batch and
speed layers as two separate code paths with separate aggregation logic.
Usage code (seeding gap events, CLI wiring, the batch/speed/serve
orchestration) belongs in `examples/run_lambda_architecture.py`, not here.

- **Do not merge `batch_layer.py` and `speed_layer.py` into one shared
  fold function.** Their duplication is intentional — it's what makes this
  a faithful Lambda demo rather than a relabeled Kappa one. If you find
  yourself wanting to share logic between them, that's a sign the change
  belongs in `data_proc.kappa` instead.
- `batch_layer.recompute_batch_view()` must stay a **full, stateless
  recompute** from the CSV snapshot + every event in the log from offset
  0 — never read or depend on the watermark/checkpoint inside it. It
  returns the new watermark (the event count at the time it ran) for the
  caller to persist; it must never persist the watermark itself.
- `speed_layer.compute_speed_increments()` only receives the already
  gap-filtered event list (events strictly after the watermark) — it must
  not read the event log, checkpoint, or watermark itself, and must not
  retain any state between calls (unlike `data_proc.kappa.state`, there is
  no persisted speed-layer state; each call recomputes the gap's
  increment from scratch, since the gap window is assumed small).
- `serving_layer.merge_views()` must stay a pure outer-join merge with no
  I/O — it decides how to reconcile batch completeness with speed
  recency, not where the inputs come from.
- If you add/rename a field produced by either layer, update both
  `batch_layer.py` and `speed_layer.py` together (so their outputs stay
  union-compatible for `serving_layer.merge_views()`), `sql/schema.sql`'s
  `lambda_batch_view`/`lambda_speed_view`/`lambda_serving_view` tables,
  and add/adjust a case in `tests/test_lambda_serving_layer.py`'s
  `test_serving_result_matches_batch_layer_once_batch_absorbs_the_gap`
  asserting the eventual-consistency property still holds.
- Persist `lambda_batch_view`/`lambda_speed_view` with
  `data_proc.etl.load.load_dataframe(..., if_exists="replace")` (each is
  fully recomputed on every run of its layer); persist
  `lambda_serving_view` with `upsert_dataframe()` instead, since it's
  keyed and should preserve customers neither layer touched this run.
