---
diataxis: explanation
---

# Data Processing Patterns — 50 Advanced Interview Questions with Answers

Target roles: Senior Data Engineer, Lead Data Engineer, Data Architect, Principal Data Engineer.

Scope: Strictly data processing patterns — batch, micro-batch, continuous streaming, incremental, parallel, distributed, stateful/stateless, windowing, partitioning, and processing reliability. Excludes data integration and organizational architecture patterns.

This page is an interview-preparation companion to
[Data processing patterns: a deeper dive](data-processing-patterns.md).
Use the deep dive for the conceptual explanations and this page for
scenario-based practice.

## Module 1: Batch, Micro-Batch, and Continuous Processing

### Q1. What are the major data processing patterns, and how do you classify them?

**Answer**


Data processing patterns can be classified along independent dimensions:

| Dimension | Patterns |
| --- | --- |
| Execution | Batch, micro-batch, continuous |
| Data scope | Full refresh, incremental |
| Compute | Sequential, parallel, distributed |
| State | Stateless, stateful |
| Time | Processing-time, event-time, window-based |
| Execution topology | Pipeline, DAG, MapReduce |
| Reliability | Checkpointed, replayable, idempotent |

A production pipeline can use several simultaneously. For example, a Spark Structured Streaming application may be distributed, incremental, micro-batch, and stateful.
### Q2. What is the difference between batch processing and micro-batch processing?

**Answer**


Batch processing operates on a bounded dataset and typically terminates after completion.

Micro-batch processing divides an ongoing input stream into successive bounded datasets and executes them repeatedly.

Example:
- Batch: Process yesterday's 500 million transactions at midnight.
- Micro-batch: Process newly arrived transactions every 10 seconds.
A key distinction is that micro-batching is an execution strategy, not necessarily a data freshness guarantee.
### Q3. When would you prefer batch processing over streaming?

**Answer**


Choose batch when:
- The business SLA allows delayed results.
- Historical reprocessing is more important than immediate updates.
- Computations involve large, bounded datasets.
- Scheduling compute only when needed is cost-effective.
- Operational simplicity outweighs low-latency requirements.
Principal-level consideration: Streaming is not inherently superior. A streaming pipeline that must maintain expensive state continuously can be less economical than periodic batch computation.
### Q4. What happens when a micro-batch takes longer than its configured trigger interval?

**Answer**


Suppose a Spark Structured Streaming query has a 10-second trigger interval, but each batch takes 25 seconds.

The engine cannot maintain the requested cadence. Subsequent batches start as soon as scheduling permits, and processing falls behind incoming data if ingestion exceeds sustainable throughput.

Consequences include growing input backlog, increasing end-to-end latency, and potentially increasing state.

Diagnostics:

```python
query.lastProgress
```



Examine batchDuration, numInputRows, inputRowsPerSecond, and processedRowsPerSecond, along with source lag and state metrics.
### Q5. Is continuous processing always faster than micro-batch processing?

**Answer**


No. Continuous processing can reduce scheduling latency, but total latency also depends on source delivery, network transfer, serialization, state access, backpressure, and sink commit behavior.

Micro-batching may achieve higher throughput through vectorized operations, efficient batching, and reduced per-record overhead.
### Q6. Explain throughput versus latency in data processing.

**Answer**


Throughput is the amount of data processed per unit time. Latency is the time taken for data to move through the relevant processing stages.

For example:
- Throughput: 100,000 records/second.
- End-to-end latency: 3 seconds.
A system can have high throughput and poor latency.

Little's Law provides a useful approximation for stable systems:
\[
L=\lambda W
\]

Where \(L\) is average work in progress, \(\lambda\) is average arrival rate, and \(W\) is average time in the system.
### Q7. What is backpressure, and how does it affect processing?

**Answer**


Backpressure occurs when downstream processing cannot keep up with upstream data production.

For example:
```text
Source:       100,000 events/sec
Processor:     60,000 events/sec
Backlog:       40,000 events/sec
```


If sustained for 10 minutes, backlog grows by approximately 24 million events.

Solutions include scaling bottleneck operators, optimizing state access, increasing effective parallelism, reducing expensive shuffles, or controlling ingestion rates.
### Q8. How would you design a processing system for both low latency and high throughput?

**Answer**


First define latency percentiles, sustained throughput, burst capacity, and correctness requirements.

Then consider:
- Partitioned processing to distribute work.
- Stateless operators before expensive stateful operations where semantics permit.
- Efficient serialization and batching.
- Sufficient operator parallelism.
- Durable state and checkpointing.
- Sink throughput and commit latency.
- Backpressure and queue monitoring.
The goal is to balance the full processing pipeline, not optimize only the source or compute engine.
## Module 2: Full Refresh and Incremental Processing

### Q9. What is the difference between full refresh and incremental processing?

**Answer**


Full refresh recomputes the entire target from a complete input dataset.

Incremental processing updates the target using only relevant changes.

For example, rebuilding a 2 TB table daily versus applying 10 GB of daily changes.

Incremental processing can reduce computation, but it introduces complexity around change tracking, deletes, corrections, and replay.
### Q10. When can full refresh be better than incremental processing?

**Answer**


Full refresh may be preferable when:
- The dataset is relatively small.
- Source change tracking is unreliable.
- Business logic frequently changes.
- Complex incremental dependencies are difficult to maintain.
- Recomputing the result is cheaper than reconciling changes.
A full refresh can also provide a useful correctness baseline against which incremental results are tested.
### Q11. How do you guarantee that incremental processing does not miss records?

**Answer**


Use a durable processing boundary such as a source offset, version, or carefully managed high-water mark.

A timestamp-based approach needs particular care because timestamps may be duplicated, delayed, or updated out of order.

A robust implementation can use a composite cursor such as (updated_at, record_id), overlap windows, and idempotent deduplication, provided the source offers the required ordering and completeness guarantees.

The cursor should advance only after successful output commit or through a recoverable protocol.
### Q12. How do you handle late-arriving records in incremental processing?

**Answer**


Possible strategies include:
- Reprocessing a rolling lookback period.
- Maintaining event-time watermarks.
- Applying corrections to previously computed results.
- Tracking source versions or sequence numbers.
- Running periodic reconciliation jobs.
Example: A transaction belonging to Monday arrives on Wednesday. If Monday's aggregate is already published, the processing system may need to update that aggregate rather than simply append Wednesday's result.
### Q13. How do you implement replay-safe incremental processing?

**Answer**


Replay safety requires repeated processing of the same input to produce the intended final result without duplicate effects.

Common techniques include deterministic event identifiers, source-version checks, idempotent upserts, and transactional writes.

A simple SQL pattern is:
```sql
MERGE INTO target t
USING source s
ON t.order_id = s.order_id
WHEN MATCHED
  AND s.version > t.version
THEN UPDATE SET
  t.amount = s.amount,
  t.version = s.version
WHEN NOT MATCHED
THEN INSERT (
  order_id, amount, version
)
VALUES (
  s.order_id, s.amount, s.version
);
```
```


The source must first be reduced to one unambiguous row per key, and version ordering must be authoritative.
### Q14. What is the difference between an incremental computation and an incremental materialized view?

**Answer**


Incremental computation is a general technique for updating results from changes rather than recomputing everything.

An incremental materialized view is a persisted query result maintained through such techniques.

For example, maintaining customer sales totals by applying transaction additions and reversals is incremental computation. Persisting and automatically maintaining the resulting aggregate table is an incremental materialized view implementation.
## Module 3: Parallel and Distributed Processing

### Q15. What is the difference between parallel processing and distributed processing?

**Answer**


Parallel processing executes multiple computations concurrently, potentially on a single machine.

Distributed processing executes across multiple networked machines and introduces additional concerns such as communication, coordination, partial failures, and distributed storage.

Distributed systems frequently use parallelism, but the terms are not interchangeable.
### Q16. Explain data partitioning and task parallelism.

**Answer**


Data partitioning divides input into subsets. Task parallelism executes processing tasks concurrently against those subsets.

For a 1 TB dataset divided into 1,000 partitions, a distributed engine can schedule many tasks concurrently, subject to available executor slots and other constraints.

Too few partitions can underutilize resources. Too many can increase scheduling overhead and create excessive small outputs.
### Q17. What is a shuffle, and why is it expensive?

**Answer**


A shuffle redistributes records across processing tasks, usually based on keys.

Operations such as GROUP BY, joins, and repartitioning may require shuffles.

Costs include network transfer, serialization, disk spilling, sorting, memory pressure, and synchronization between stages.

Example Spark physical plan:
```text
HashAggregate
  Exchange hashpartitioning(customer_id, 200)
    HashAggregate
      FileScan parquet
```

The Exchange represents a shuffle boundary.
### Q18. What is the difference between narrow and wide transformations?

**Answer**


A narrow transformation can compute each output partition using a limited set of input partitions without requiring a global redistribution.

Examples include many filter, map, and projection operations.

A wide transformation creates dependencies across partitions and commonly requires a shuffle.

Examples include groupBy, distinct, and many joins.
### Q19. How do you handle data skew in distributed processing?

**Answer**


Data skew occurs when some tasks process disproportionately more data than others.

Solutions include:
- Adaptive query execution.
- Broadcasting an eligible small join side.
- Salting heavily skewed keys.
- Pre-aggregation.
- Splitting hot-key processing.
- Choosing better partition keys.
Interview scenario: One Spark task runs for 20 minutes while the other 199 tasks finish in 30 seconds. Investigate task input sizes, shuffle read distributions, spills, and key frequencies before increasing cluster size.
### Q20. What is the difference between repartition and coalesce in Spark?

**Answer**


repartition() redistributes data through a shuffle and can increase or decrease the partition count.

coalesce() commonly reduces partitions using narrower dependencies and avoids a full shuffle, although it can produce uneven partition sizes.

```python
df.repartition(200, "customer_id")
df.coalesce(20)
```


Use repartitioning when balanced distribution or key-based grouping matters. Use coalescing when reducing output partition count without full redistribution is appropriate.
### Q21. Explain broadcast processing.

**Answer**


Broadcast processing replicates a small dataset across worker nodes so larger distributed datasets can be processed locally against it.

For joins, this can avoid shuffling the large side.

```python
from pyspark.sql.functions import broadcast

result = orders.join(
    broadcast(customers),
    "customer_id",
)
```



Broadcasting is effective only when the replicated dataset fits available resources and the join semantics are supported.
### Q22. How does MapReduce relate to modern DAG-based processing?

**Answer**


MapReduce organizes computation into map, shuffle, and reduce phases.

Modern DAG-based engines generalize this model by representing computations as graphs of operators and stages. They can optimize execution pipelines and avoid materializing every intermediate result.

Spark still uses map-like transformations, exchanges, and aggregation stages, but is not limited to a single MapReduce sequence.
## Module 4: Stateful, Stateless, and Window-Based Processing

### Q23. What is stateful processing?

**Answer**


Stateful processing maintains information from previous records to influence future results.

Examples include running totals, deduplication, session detection, streaming joins, and fraud detection.

State introduces memory or disk requirements, checkpointing, recovery, serialization, and cleanup concerns.
### Q24. Why is stateful processing harder to scale than stateless processing?

**Answer**


Stateless processing can often redistribute work freely.

Stateful processing must preserve the relationship between keys and their state. Scaling may require transferring or restoring state across workers.

Large state can increase checkpoint duration, recovery time, storage usage, and operational complexity.
### Q25. What is keyed state?

**Answer**


Keyed state stores independent state associated with each logical key.

For example:
customer_101 → transaction_count = 15
customer_102 → transaction_count = 8
customer_103 → transaction_count = 21


Key-based partitioning ensures records for a given key are processed consistently by the responsible operator instance.
### Q26. What is the difference between event time and processing time?

**Answer**


Event time represents when an event occurred according to its timestamp.

Processing time represents when the processing system handles it.

A transaction created at 10:00 but processed at 10:07 has a seven-minute difference.

Event-time processing is important when analytical correctness depends on business occurrence time rather than arrival time.
### Q27. Explain tumbling, sliding, and session windows.

**Answer**

| Window | Behavior | Example |
| --- | --- | --- |
| Tumbling | Fixed-size, non-overlapping | Revenue every 5 minutes |
| Sliding | Fixed-size, overlapping | Previous 10 minutes, updated every minute |
| Session | Variable-length, inactivity-based | User browsing session |

Window choice affects result semantics, state size, update frequency, and late-data handling.
### Q28. What is a watermark?

**Answer**


A watermark represents a processing engine's estimate of event-time progress.

It helps determine when event-time results can be finalized or state can be cleaned up, according to the engine's semantics.

A watermark is not a guarantee that no older events will arrive.

For example, a ten-minute watermark delay allows a streaming aggregation to tolerate a defined amount of event-time disorder, subject to the specific engine and operator.
### Q29. What happens when a late event arrives after its window state has been removed?

**Answer**


The event may be dropped from the window computation or handled through an alternative late-data mechanism, depending on the framework and configuration.

A production design may need a correction path, late-event side output, or historical reconciliation process.

This is a correctness decision, not merely a performance setting.
### Q30. How do you prevent unbounded state growth?

**Answer**


Use bounded windows, watermarks, state TTL, appropriate join constraints, and explicit state cleanup.

Also monitor state row counts, state size, checkpoint duration, and recovery time.

TTL must be chosen carefully: expiring state too early can change business results or permit duplicate processing.
### Q31. How do you implement deduplication in stream processing?

**Answer**


Use stable event identifiers and track previously processed IDs.

For example:

```python
deduplicated = (
    events
    .withWatermark("event_time", "15 minutes")
    .dropDuplicates(["event_id", "event_time"])
)
```



This example deduplicates the specified combination within the applicable state-retention semantics. It does not necessarily deduplicate all events sharing event_id if their event timestamps differ.

The deduplication key and retention horizon must match the business requirement.
### Q32. Why are stream-stream joins more complex than batch joins?

**Answer**


Both inputs are potentially unbounded.

The engine must retain records from each side until matching records can arrive or until it is safe to expire them.

Time constraints and watermarks are commonly used to bound state.

Without appropriate bounds, state can grow indefinitely.
## Module 5: Reliability and Fault-Tolerant Processing

### Q33. Explain at-most-once, at-least-once, and exactly-once processing.

**Answer**

| Guarantee | Meaning |
| --- | --- |
| At-most-once | Data may be lost, but is not retried for duplicate processing |
| At-least-once | Data is retried, so duplicate processing is possible |
| Exactly-once | Each logical input has exactly one effect within the defined guarantee boundary |

Exactly-once guarantees must always specify their scope. Internal engine state consistency does not automatically imply exactly-once external side effects.
### Q34. What is checkpointing?

**Answer**


Checkpointing persists enough processing progress and state to resume after failure.

A checkpoint may include source positions, operator state, and recovery metadata.

A successful checkpoint creates a recoverable processing boundary, but external sink consistency depends on the sink protocol.
### Q35. What is the difference between checkpointing and replay?

**Answer**


Checkpointing stores processing progress and state.

Replay reprocesses previously retained input.

A system may restore a checkpoint and replay records after that checkpoint to recover the correct state.

Replay requires sufficient input retention and deterministic or appropriately controlled processing behavior.
### Q36. What is idempotent processing?

**Answer**


An operation is idempotent if applying it multiple times has the same intended effect as applying it once.

For example:
```sql
UPDATE accounts
SET status = 'ACTIVE'
WHERE account_id = 100;
```

Repeatedly setting the same status is idempotent.

By contrast:
```sql
UPDATE accounts
SET balance = balance + 100
WHERE account_id = 100;
```

This is not idempotent because repeated execution changes the balance repeatedly.
### Q37. How do you prevent duplicate output after a processing failure?

**Answer**


Possible mechanisms include:
- Transactional output commits.
- Stable batch or event identifiers.
- Idempotent upserts.
- Deduplication against durable state.
- Coordinated source progress and sink commits.
For Spark foreachBatch, repeated execution of a batch is possible. The sink operation must therefore be designed to tolerate replay.
### Q38. How does a processing engine recover from worker failure?

**Answer**


A distributed processing engine detects task or worker failure, reschedules work, and reconstructs the necessary state or intermediate results.

Stateless tasks can often be recomputed directly.

Stateful tasks may require checkpoint restoration and source replay.

Recovery time depends on state size, checkpoint storage, parallelism, and source/sink availability.
### Q39. What is deterministic processing, and why does it matter?

**Answer**


Deterministic processing produces the same result for the same logical inputs and relevant execution context.

Nondeterministic operations such as uncontrolled randomness, current timestamps, or unordered tie-breaking can make replay produce different results.

For example, selecting the latest record should use a complete, deterministic ordering rather than an ambiguous timestamp alone.
### Q40. How do you test processing correctness under failure?

**Answer**


Use controlled failure injection:
- Kill workers during processing.
- Restart jobs after output writes.
- Replay the same input.
- Introduce duplicates and out-of-order events.
- Simulate state recovery.
- Compare final output against a trusted reference result.
Verify business invariants, not only whether the job restarts successfully.
## Module 6: Principal Data Engineer Scenario Questions

### Q41. A daily batch job processes 2 TB and takes six hours. How would you optimize it?

Model answer:

First profile the execution plan and identify whether the bottleneck is input scanning, shuffle, skew, memory spills, output writes, or compute availability.

Then consider partition pruning, column pruning, predicate pushdown, incremental processing, broadcast joins, better partition sizing, and reducing repeated computations.

Measure before and after changes using stage duration, shuffle bytes, spill metrics, input volume, and cost per run.

Avoid assuming that adding workers will solve an inefficient execution plan.
### Q42. A streaming pipeline has growing latency even though CPU utilization is low. What would you investigate?

Model answer:

Low CPU utilization does not rule out bottlenecks.

Investigate source partition parallelism, network waits, sink commit latency, checkpoint pauses, state-store I/O, task skew, and scheduling delays.

Compare input rate against processing rate and inspect per-operator metrics.

A single hot partition or slow sink can limit the entire pipeline while most workers remain idle.
### Q43. A Spark aggregation runs quickly for most partitions, but one task takes 30 minutes. What is the likely cause?

Model answer:

A common cause is skewed data distribution.

Check task-level input sizes, shuffle read volume, spills, and key frequency.

If a single key dominates, consider partial aggregation, skew-aware partitioning, or salting where mathematically valid.

Increasing executor count alone may not help because one oversized partition remains a single bottleneck.
### Q44. A stateful streaming job crashes after several days due to memory pressure. How would you fix it?

Model answer:

Inspect state size, key cardinality, TTL configuration, watermark progress, and checkpoint behavior.

Determine whether state is growing because of missing expiration, idle input partitions, unbounded joins, or increasing business cardinality.

Introduce appropriate state bounds and cleanup policies without violating correctness.

Consider a disk-backed state store and evaluate checkpoint and recovery costs.
### Q45. A pipeline produces duplicate business transactions after restart. How would you investigate?

Model answer:

Identify the exact failure boundary: input read, state update, output write, or progress commit.

Check whether output was successfully written before the failure and whether the same input was replayed.

Then examine sink idempotency, transaction identifiers, deduplication keys, and commit coordination.

The correct solution depends on whether the duplicate is in internal computation, persisted output, or an external business side effect.
### Q46. How would you process one billion events per day with a five-second freshness SLA?

Model answer:

One billion events per day averages approximately 11,574 events per second, but peak throughput may be much higher.

I would first establish peak rate, event size, partition-key distribution, state requirements, and latency percentiles.

Then design a partitioned streaming pipeline with sufficient parallelism, bounded state where possible, durable checkpoints, and a sink capable of meeting the throughput target.

Load-test burst traffic and recovery, and monitor p95/p99 end-to-end latency rather than relying only on average throughput.
### Q47. A micro-batch pipeline has a 10-second trigger but takes 45 seconds per batch. What would you do?

Model answer:

Determine whether the delay comes from source reads, transformations, shuffles, state processing, or sink writes.

Inspect batch progress and Spark UI metrics.

Optimize the dominant bottleneck and adjust parallelism or resource allocation.

Increasing the trigger interval may reduce scheduling overhead, but it does not fix a sustained throughput deficit.
### Q48. How would you safely reprocess 30 days of historical data without corrupting current results?

Model answer:

Define the reprocessing scope and source-of-truth version.

Use isolated staging outputs or versioned partitions where practical.

Make transformations deterministic and output commits idempotent.

Validate row counts, key uniqueness, aggregates, and business invariants before replacing or reconciling production results.

Coordinate historical corrections with live processing to avoid stale data overwriting newer results.
### Q49. How would you choose between stateful streaming aggregation and periodic batch aggregation?

Model answer:

Compare freshness requirements, state cardinality, input volume, recovery requirements, cost, and correction behavior.

Stateful streaming is suitable when aggregates must update frequently and retained state can be managed.

Periodic batch aggregation is attractive when latency requirements are relaxed or historical recomputation is simpler.

A hybrid approach may maintain recent aggregates continuously while periodically reconciling them against authoritative historical data.
### Q50. Design a fault-tolerant distributed processing system that supports high throughput, low latency, and historical replay.

Model answer:

I would separate the requirements into five areas.

1. Input and execution: Use partitioned, replayable input and choose batch, micro-batch, or continuous processing according to the latency target.

2. Parallelism: Distribute processing by suitable keys, minimize unnecessary shuffles, and identify hot-key risks.

3. State: Use durable state management with checkpointing, recovery, and explicit expiration policies.

4. Output correctness: Implement transactional or idempotent output handling and clearly define exactly-once guarantee boundaries.

5. Operations: Monitor throughput, lag, latency percentiles, state size, checkpoint duration, task failures, and processing cost.

I would validate the design using peak-load testing, replay tests, worker failures, duplicate input, late events, and sink outages.

## Self-assessment — Principal Data Engineer readiness

### 5-question knowledge check

0 of 5 answered

1. Can micro-batch processing also be incremental?

No, they are different alternatives

Yes, they describe different dimensions

Only for batch sources



2. A streaming job has one hot key and 99 idle workers. What should you investigate first?

Add 100 workers

Increase trigger interval

Partition-key skew and per-task metrics



3. Which mechanism alone guarantees exactly-once external API side effects?

Checkpointing

A watermark

Neither



4. A watermark advances past a window. What does it guarantee?

No older events can ever arrive

The engine can apply configured late-data and cleanup semantics

All external sinks have committed



5. What is the best first step when a 2 TB batch job slows down?

Double cluster size

Inspect execution plans and task metrics

Convert it to streaming
