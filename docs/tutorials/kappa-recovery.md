---
diataxis: tutorial
---

# Retry a Kappa run after a checkpoint write fails

Use a test to interrupt the real Kappa processing function after it
commits the summary and saves order state. The exercise uses temporary
files and in-memory SQLite.

## 1. Run the recovery test

From the repository root, run the named test with the project's dev
dependencies installed.

```bash
uv run pytest -q tests/test_kappa_checkpoint_and_state.py::test_retry_after_checkpoint_write_failure_keeps_summary
```

Expect `1 passed`. The injected error occurs when the demo tries to
write the checkpoint, after the summary transaction has finished.

## 2. Trace the retry in the test

Open `tests/test_kappa_checkpoint_and_state.py` and find
`test_retry_after_checkpoint_write_failure_keeps_summary`. Compare the
assertions before and after the second call to `process()`.

| When | Saved order IDs | Checkpoint | Summary row (customer ID, order count, spend) |
| --- | --- | ---: | --- |
| After the simulated failure | 1 | 0 | `(1, 1, 10.0)` |
| After retry | 1 | 1 | `(1, 1, 10.0)` |

The retry reads the same event again because the checkpoint is still
zero. The fold sets the order state by order ID, then the upsert
replaces the customer summary row. The count and spend stay the same.

This exercise covers a single reader and a failure before the checkpoint
write starts. The database, order state file, and checkpoint are separate
writes. A partially written state file and concurrent runs have different
failure modes. The [demo reference](../reference/demos.md) describes
which files Kappa rebuilds during a full replay.
