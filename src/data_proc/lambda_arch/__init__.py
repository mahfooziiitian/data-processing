"""Lambda-architecture building blocks: separate batch and speed layers,
unified at query time by a serving layer.

Unlike `data_proc.kappa` (one unified stream path that also handles
replay), this package deliberately keeps two independent processing
paths, faithfully reproducing Lambda's defining trade-off and its
best-known criticism — the same business logic (aggregating orders per
customer) is implemented twice:

  * `batch_layer` — slow but always-correct: a full, stateless recompute
    from the entire historical dataset every time it runs.
  * `speed_layer` — fast but only covers the "gap": processes only the
    events appended since the batch layer's last watermark, so it can run
    far more often than the batch layer.
  * `serving_layer` — merges both views at query time so callers get
    batch-layer completeness plus speed-layer recency without the batch
    layer needing to run in real time.
  * `watermark` — tracks the event-log offset the batch layer has fully
    covered, so the speed layer knows where its "gap" starts.

This is a library package: reusable building blocks only. The runnable
demo that wires these together lives in
`examples/run_lambda_architecture.py`.
"""
