---
diataxis: explanation
---

# Data Processing Patterns — Company-Style Mock Interviews

Target roles: Senior Data Engineer, Staff Data Engineer, Principal Data
Engineer, Data Architect.

Scope: Data processing patterns only — distributed batch, incremental
computation, skew handling, event-time windowing, stateful processing,
fault tolerance, and the performance/cost trade-offs behind each choice.

The scenarios below are written in the style of interviews at
well-known, high-scale companies (Walmart, Google, Amazon, Microsoft,
Netflix, Uber, Databricks). They are **illustrative, company-styled
practice scenarios**, not verified or leaked questions from any
company's actual interview process. Numbers such as record counts,
latencies, and cluster sizes are assumptions for the exercise, not
published production metrics.

This page complements the other two pages in this series:

- [Data processing patterns: a deeper dive](data-processing-patterns.md)
  — the conceptual reference for every pattern named here.
- [50 advanced interview questions with answers](data-processing-patterns-interview.md)
  — a self-paced question bank organized by topic rather than by
  company.

## How to use this page

For each scenario, practice answering in three layers — that is what
separates an architect-level answer from a framework-level answer:

1. **The processing algorithm** — what computation is actually
   happening (aggregation, join, windowing, dedup)?
2. **Its distributed execution behavior** — how does the work get
   partitioned, shuffled, and parallelized, and where are the likely
   bottlenecks?
3. **Its failure and correctness guarantees** — what happens on retry,
   late data, out-of-order events, or partial failure, and how do you
   prove the result is still correct?

## Part 1: Company-specific question banks

Each entry below is a condensed prompt with the key ideas an
architect-level answer should cover. The [full mock interview](#part-4-full-mock-interview-walmart-global-tech-principal-data-engineer)
later on this page works through ten Walmart-style questions at that
level of depth; apply the same structure when practicing the other
companies.

### 1. Walmart Global Tech — large-scale retail data processing

Focus: high-volume batch processing, incremental aggregation,
partitioning, skew, and distributed Spark optimization.

**Q1.** Walmart processes 5 billion retail transactions daily. How
would you design the data processing layer?

- Calculate average throughput (≈58K transactions/second), then size
  for peak traffic.
- Partition data by appropriate business and processing dimensions.
- Use distributed processing for transformation and aggregation.
- Prefer incremental computation over repeatedly scanning full history.
- Define correctness for returns, cancellations, and late transactions.
- Monitor processing latency, shuffle, spills, and compute cost.

*Follow-up: what changes if Black Friday traffic is 15× normal peak?*

**Q2.** A Spark job processes sales across 10,000 stores. One store
contributes 30% of transactions. How would you handle the data skew?

Discuss hot-key detection, map-side partial aggregation, key salting,
Adaptive Query Execution, and the trade-offs of repartitioning.

*Follow-up: why might increasing executor count fail to solve the
problem?*

**Q3.** A daily sales aggregation is recomputed from 10 TB of
historical data. How would you convert it into incremental processing?

Explain change tracking, affected-partition recomputation, correction
handling, idempotent output, and reconciliation against a full-refresh
baseline.

**Q4.** How would you compute hourly sales totals when transactions
can arrive up to 48 hours late?

Discuss event-time windows, watermark policy, state retention,
correction processing, and finalization semantics.

**Q5.** A distributed sales aggregation takes 90 minutes, with 70% of
execution time spent in shuffle. How would you optimize it?

Explain physical plans, partial aggregation, partition sizing, skew,
spill metrics, and avoiding unnecessary redistribution.

### 2. Google — distributed processing and algorithmic correctness

Focus: distributed computation, MapReduce, DAG execution, event time,
windowing, and fault tolerance.

**Q6.** Design a distributed algorithm to calculate the top 100 search
queries from 100 billion records.

1. Partition the input across workers.
2. Calculate local query frequencies.
3. Shuffle partial counts by query key.
4. Aggregate global frequencies.
5. Compute local top-K candidates and merge them into a global top 100.
6. Define deterministic tie-breaking and account for hot keys.

*Follow-up: how would the solution change if approximate answers were
acceptable?*

**Q7.** Explain how MapReduce achieves fault tolerance when a worker
fails during a shuffle-heavy computation.

Cover task retries, intermediate output availability, recomputation,
deterministic operations, and coordinator recovery assumptions.

**Q8.** How would you process out-of-order clickstream events while
producing accurate five-minute session metrics?

Discuss event-time timestamps, watermarks, window assignment, allowed
lateness, and retractions or corrections.

**Q9.** How would you implement a distributed `GROUP BY` efficiently
when one key appears in 40% of records?

Explain local combiners, hierarchical aggregation, skew-aware
partitioning, and the limitations of simply hashing by key.

**Q10.** How would you design a processing system that supports
replaying one month of events without producing inconsistent results?

Cover deterministic computation, versioned logic, durable checkpoints,
replay boundaries, and transactional or idempotent outputs.

### 3. Amazon — high-scale processing and operational reliability

Focus: distributed processing, peak-load handling, state management,
fault recovery, and cost/performance trade-offs.

**Q11.** Amazon processes hundreds of millions of order events daily.
How would you calculate near-real-time revenue with cancellations and
refunds?

Use an event-driven incremental computation model with stable
transaction IDs and explicit revenue-adjustment semantics. Define how
original purchases, cancellations, refunds, and corrections affect
aggregates. Handle duplicate and out-of-order events, maintain
recoverable state, and verify results through reconciliation.

*Follow-up: how do you prevent a refund from being applied twice?*

**Q12.** Your processing system receives 200,000 events/sec but can
process only 120,000. How would you diagnose and resolve the backlog?

Discuss sustainable throughput, partition parallelism, operator
bottlenecks, state-store performance, batching, and sink capacity.

**Q13.** A stateful aggregation crashes after processing 50 million
events. How do you recover without losing or double-counting data?

Explain checkpoint restoration, source replay, state consistency, and
output commit guarantees.

**Q14.** How would you choose between hourly batch processing and
continuous stream processing for inventory analytics?

Evaluate freshness SLA, operational complexity, correction handling,
state size, recovery time, and cost.

**Q15.** A processing job is retrying after failure and causes
duplicate customer charges. What is wrong with the processing design?

Distinguish internal exactly-once state recovery from exactly-once
*external business effects*. Discuss idempotency keys and atomic
business operations.

### 4. Microsoft — enterprise-scale distributed processing

Focus: Spark internals, memory management, execution planning,
incremental computation, and reliability.

**Q16.** A Spark job has 500 tasks, but only 20 are actively running.
How would you diagnose underutilization?

Investigate available executor slots, partition counts, scheduling
constraints, skew, stage dependencies, and source parallelism.

**Q17.** How would you optimize a distributed join between a 5 TB fact
dataset and a 50 MB dimension dataset?

Explain broadcast join eligibility, memory considerations, column
pruning, filtering, and physical-plan verification.

**Q18.** Explain how Spark's DAG scheduler handles stage failures and
recomputation.

Discuss lineage, shuffle boundaries, task retries, lost shuffle
outputs, and recovery limitations.

**Q19.** How would you implement a processing job that supports
incremental updates and periodic full reconciliation?

Explain authoritative input versions, deterministic transformations,
comparison checks, and safe target replacement.

**Q20.** A Spark aggregation is spilling 200 GB to disk. What metrics
and processing changes would you investigate?

Cover hash aggregation, shuffle partition sizes, skew, executor memory,
spill behavior, and aggregation cardinality.

### 5. Netflix — streaming and event-time processing

Focus: continuous processing, event-time semantics, session windows,
stateful computation, and recovery.

**Q21.** Netflix wants to calculate concurrent viewers by region every
10 seconds. How would you design the processing logic?

Define what constitutes an active viewer, session start/stop behavior,
heartbeat expiry, keyed state, and windowed output.

**Q22.** A user watches content on multiple devices. How would you
compute unique active users without double-counting?

Discuss deduplication by user ID, event-time windows, exact versus
approximate distinct counts, and memory trade-offs.

**Q23.** How would you handle streaming events that arrive 30 minutes
late while preserving accurate viewing analytics?

Explain event-time processing, watermark policies, correction outputs,
and the trade-off between finality and latency.

**Q24.** A streaming application's state grows continuously for seven
days. What could cause it?

Discuss missing expiration, unbounded joins, stalled watermarks,
excessive key cardinality, and state cleanup.

**Q25.** How would you replay historical viewing events after changing
sessionization logic?

Discuss versioned processing, deterministic replay, output isolation,
and reconciling new session results with existing data.

### 6. Uber — geospatial and real-time stateful processing

Focus: low-latency processing, keyed state, out-of-order events,
partitioning, and skew.

**Q26.** Uber receives millions of driver-location updates per second.
How would you process them with low latency?

Partition updates by driver or spatial key according to the operation,
use stateless filtering where possible, maintain only required
latest-location state, and define expiration for inactive drivers.
Measure per-key skew, processing latency, state size, and update
throughput.

**Q27.** How would you calculate active drivers per geographic region
every five seconds?

Discuss keyed state, location changes, entering/exiting regions,
duplicate updates, and consistent aggregate maintenance.

**Q28.** Driver-location updates arrive out of order. How do you
prevent an older update from overwriting the latest location?

Use authoritative event ordering such as per-driver sequence numbers or
suitable version metadata. Apply updates only when they are newer than
retained state.

**Q29.** One geographic region receives 100 times more events than
others. How would you avoid a processing hotspot?

Explain spatial partitioning, hot-region splitting, hierarchical
aggregation, and balancing correctness against parallelism.

**Q30.** How would you process trip-duration metrics when
trip-completion events can be delayed or duplicated?

Discuss stable trip IDs, keyed state, event-time ordering,
deduplication, expiration, and reconciliation.

### 7. Databricks — Spark and lakehouse processing internals

Focus: Catalyst, physical plans, shuffle optimization, incremental
computation, stateful streaming, and Delta Lake processing.

**Q31.** Explain the physical execution plan of a Spark SQL `GROUP BY`
on a 2 TB table.

A typical plan includes a scan, optional filtering and projection,
partial aggregation, shuffle exchange, and final aggregation:

```text
HashAggregate (final)
  Exchange hashpartitioning(key)
    HashAggregate (partial)
      FileScan
```

Discuss shuffle bytes, aggregation cardinality, spills, skew, and
Adaptive Query Execution.

**Q32.** What is the difference between Spark batch execution and
Structured Streaming micro-batch execution?

Explain bounded execution, repeated micro-batch planning, source
progress tracking, checkpointing, state stores, and output commit
behavior.

**Q33.** A streaming aggregation's state store has grown to 500 GB. How
would you optimize it?

Investigate key cardinality, watermark advancement, state retention,
operator semantics, checkpoint cost, and state-store backend
selection.

**Q34.** How would you design a replay-safe `foreachBatch` computation?

Explain batch replay, deterministic input preparation, idempotent sink
writes, and safe transaction boundaries.

**Q35.** A Spark job processes 1 TB in 15 minutes but becomes slower
after doubling cluster size. Why?

Investigate excessive partitioning, scheduling overhead, network
contention, shuffle behavior, skew, and changes in execution plans.

## Part 2: Cross-company principal-level system design scenarios

These scenarios are particularly useful for Staff/Principal Data
Engineer and Data Architect interviews, across any company.

| # | Scenario | Core evaluation |
| --- | --- | --- |
| 36 | Design a processing engine for 10 billion events/day | Throughput, partitioning, backpressure |
| 37 | Reduce a 4-hour batch workload to 30 minutes | Physical plans, parallelism, shuffle |
| 38 | Design an incremental aggregation with 72-hour late corrections | State, replay, correctness |
| 39 | Handle 100× traffic spikes without losing processing progress | Backpressure, capacity, recovery |
| 40 | Migrate a full-refresh pipeline to incremental processing | Change tracking, reconciliation |
| 41 | Design a distributed top-K algorithm for skewed input | Combiners, aggregation, memory |
| 42 | Recover a stateful job after losing multiple workers | Checkpoints, replay, recovery time |
| 43 | Maintain accurate sliding-window metrics at scale | Window fan-out, state management |
| 44 | Optimize a pipeline with 80% time spent on shuffles | Partitioning, join strategy, AQE |
| 45 | Support deterministic historical recomputation | Replay, ordering, versioned logic |
| 46 | Process 100 TB/day with a strict cost budget | Throughput, resource efficiency |
| 47 | Handle duplicate, missing, and out-of-order events | Deduplication, state, reconciliation |
| 48 | Scale stateful processing from 20 to 200 workers | State redistribution, checkpointing |
| 49 | Achieve p99 processing latency under 500 ms | Tail latency, bottleneck isolation |
| 50 | Design a fault-tolerant batch + streaming processing platform | Correctness, recovery, trade-offs |

## Part 3: Company focus matrix

Illustrative preparation priorities, not measured interview
frequencies.

| Company | Most important preparation topics |
| --- | --- |
| Walmart | Batch optimization, incremental processing, skew |
| Google | Distributed algorithms, MapReduce, event-time correctness |
| Amazon | Scalability, fault tolerance, processing reliability |
| Microsoft | Spark DAG, memory, distributed joins |
| Netflix | Streaming, windows, state, late events |
| Uber | Real-time state, key partitioning, event ordering |
| Databricks | Catalyst, AQE, state stores, micro-batch internals |

## Part 4: Full mock interview — Walmart Global Tech, Principal Data Engineer

This section is a simulated Principal Data Engineer interview built
around large-scale retail processing scenarios. The questions are
designed around engineering challenges relevant to Walmart-scale
workloads — they are **not represented as verified questions from
actual Walmart interviews**.

Interview expectations: for each problem, demonstrate algorithmic
correctness, distributed execution knowledge, performance
optimization, fault tolerance, and architectural trade-offs. Apply the
same structure to practice a mock interview for any of the other
companies listed in Part 1.

### Interview overview

| # | Scenario | Primary processing pattern |
| --- | --- | --- |
| 1 | Process 5 billion sales transactions daily | Distributed batch and incremental |
| 2 | Black Friday data skew | Parallel aggregation and skew handling |
| 3 | Optimize a 10 TB Spark aggregation | DAG, shuffle, and partial aggregation |
| 4 | Late-arriving retail transactions | Event-time window processing |
| 5 | Incremental processing with corrections | Incremental computation |
| 6 | Optimize massive fact-to-dimension joins | Broadcast and shuffle joins |
| 7 | Stateful processing at massive scale | Stateful vs. stateless processing |
| 8 | Recover from a mid-processing failure | Checkpointing and deterministic replay |
| 9 | Scale micro-batch processing under load | Backpressure and throughput |
| 10 | Design a cost-efficient 100 TB/day processing platform | End-to-end processing architecture |

### Question 1 — Process 5 billion retail transactions daily

Difficulty: Principal.

**Interviewer:** Walmart processes 5 billion retail transaction records
per day across stores and online channels. Design a processing system
that computes daily revenue, transaction counts, and store-level
aggregates. The results must be available within 30 minutes of the end
of each day. Explain your processing strategy, partitioning, Spark
execution plan, failure recovery, and cost optimizations.

**Model answer**

*Step 1: estimate workload size.* Assuming each transaction record
averages 500 bytes: ≈2.5 TB raw logical data per day, ≈58K
records/second average rate, with a 30-minute SLA after day-end. These
are illustrative assumptions, not actual production metrics.

*Step 2: choose the processing pattern.* Use incremental distributed
batch processing, with periodic aggregation of newly available
transactions and a final daily reconciliation. This avoids scanning
the entire historical dataset every day:

```text
Partitioned transaction dataset (sales_date, store, channel)
  → Spark distributed processing (filter → partial aggregate → shuffle → final aggregate)
  → Daily store revenue aggregates (store_id, sales_date, total_revenue, transaction_count)
```

*Step 3: implement with PySpark.*

```python
from pyspark.sql import functions as F

transactions = (
    spark.read.table("retail.transactions")
    .where(F.col("sales_date") == "2026-11-04")
    .select("store_id", "sales_date", "transaction_id", "net_amount")
)

daily_sales = (
    transactions
    .groupBy("store_id", "sales_date")
    .agg(
        F.sum("net_amount").alias("total_revenue"),
        F.count("*").alias("transaction_count"),
    )
)

daily_sales.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "sales_date = '2026-11-04'") \
    .saveAsTable("retail.daily_sales")
```

This assumes the input is already transaction-level, unique, and
represents finalized net sales. Returns, corrections, and source
duplicates would require additional handling. The target must be a
compatible Delta table, and the partition-scoped overwrite must be
supported and correctly configured.

*Step 4: explain the physical execution plan.*

```text
AdaptiveSparkPlan
+- HashAggregate
   Keys: store_id, sales_date
   Functions: sum, count
   +- Exchange hashpartitioning(store_id, sales_date, N)
      +- HashAggregate
         Keys: store_id, sales_date
         Functions: partial_sum, partial_count
         +- Project
            +- Filter sales_date = ...
               +- FileScan parquet/delta
```

Important execution details: partition pruning limits input scanning,
column pruning reduces data read, partial aggregation reduces shuffle
volume, the exchange redistributes partial aggregates by grouping
keys, and the final aggregation combines results. This is an
illustrative plan — actual operators depend on Spark version, data
types, configuration, and Adaptive Query Execution.

*Step 5: optimize the workload.* Use columnar storage, partition
pruning, partial aggregation, appropriately sized files, and adaptive
execution. Avoid blindly partitioning the physical table by
`store_id`, because high-cardinality partitioning can create excessive
directories and small files. Instead, evaluate date partitioning and
clustering or data-layout optimizations based on measured query
patterns.

*Step 6: validate the SLA.* Track source data completeness at the
daily cutoff, input rows/bytes, shuffle read/write bytes, spill size,
stage duration and task skew, output commit time, and end-to-end
freshness.

**Principal-level trade-off:** the 30-minute SLA requires a defined
completeness policy. If transactions can arrive hours late, the system
must distinguish preliminary results from finalized results and
support corrections.

**Interviewer follow-ups**

- *Would you process all 5 billion records in one Spark job?* Not
  necessarily — evaluate incremental aggregation throughout the day to
  reduce day-end workload, with a bounded final reconciliation.
- *Would 1,000 executors guarantee the SLA?* No. Partition count,
  skew, shuffle behavior, I/O throughput, and output bottlenecks can
  prevent effective scaling.
- *How do you avoid double-counting during retry?* Use deterministic
  input selection and idempotent partition replacement or
  transactional aggregate updates.

### Question 2 — Black Friday data skew

**Interviewer:** During Black Friday, one extremely popular product
accounts for 35% of 2 billion transaction records. A Spark aggregation
by `product_id` has 500 shuffle partitions. Most tasks finish in 40
seconds, but one task takes 25 minutes. How would you diagnose and fix
it?

**Model answer**

This is a classic hot-key skew problem. The first step is to identify
the processing operator responsible for the bottleneck. For an
associative aggregation such as `SUM`, Spark may already perform
partial aggregation before shuffling — so a hot key does not
automatically imply that all its original rows are sent to one
reducer. Inspect the actual physical plan and task metrics before
deciding whether salting is necessary.

*Diagnostics:*

```python
sales.groupBy("product_id") \
    .agg(F.sum("amount")) \
    .explain("formatted")

# Check Spark UI for task duration, shuffle bytes, spill, and skewed
# partition sizes, then inspect key frequency:
sales.groupBy("product_id") \
    .count() \
    .orderBy(F.desc("count")) \
    .show(20)
```

*Solution: two-stage salted aggregation.* For an aggregation where a
hot key remains a bottleneck, distribute its workload across
deterministic salt buckets:

```python
from pyspark.sql import functions as F

salted = sales.withColumn(
    "salt", F.pmod(F.xxhash64("transaction_id"), F.lit(32))
)

partial = (
    salted
    .groupBy("product_id", "salt")
    .agg(F.sum("amount").alias("partial_revenue"))
)

final = (
    partial
    .groupBy("product_id")
    .agg(F.sum("partial_revenue").alias("total_revenue"))
)
```

The `transaction_id` must be non-null and sufficiently distributed for
salting to work effectively.

```text
Final HashAggregate(product_id)
  Exchange hashpartitioning(product_id)
    Partial HashAggregate(product_id)
      HashAggregate(product_id, salt)
        Exchange hashpartitioning(product_id, salt)
          Partial HashAggregate(product_id, salt)
            Project(product_id, salt, amount)
              FileScan
```

Spark may combine or alter some operators through optimization.

**Trade-offs**

| Approach | Benefit | Risk |
| --- | --- | --- |
| Increase shuffle partitions | More overall parallelism | Hot key may remain concentrated |
| Salting | Distributes hot-key work | Additional aggregation/shuffle |
| Partial aggregation | Reduces intermediate data | May already be optimized |
| AQE skew optimization | Helps supported skewed operations | Not a universal fix for aggregations |
| Pre-aggregate upstream | Reduces data volume | Changes processing topology |

**Principal-level answer:** first verify whether the bottleneck is
truly skew in final aggregation, skewed input tasks, spill, or another
stage. Salting is justified only when the measured cost exceeds its
extra shuffle overhead.

**Interviewer follow-ups**

- *Can salting change the result of `AVG`?* Yes, if partial averages
  are averaged directly. Preserve partial sums and counts, then
  compute `SUM(sum) / SUM(count)`.
- *Can you salt `COUNT(DISTINCT customer_id)` the same way?* Not by
  summing distinct counts from independent salt buckets, unless each
  customer is guaranteed to map to exactly one bucket for that
  aggregation scope. Otherwise, use exact set semantics or an
  appropriate approximate-distinct algorithm.

### Question 3 — Optimize a 10 TB Spark aggregation

**Interviewer:** A Spark batch job processes 10 TB of sales data,
aggregates revenue by store and product category, and takes four
hours. The business requires completion within 45 minutes. How would
you optimize it?

**Model answer**

Approach this as a distributed execution optimization problem, not
immediately as a cluster-sizing problem.

*Step 1: analyze the physical plan.*

```sql
EXPLAIN FORMATTED
SELECT
    store_id,
    category_id,
    SUM(net_amount) AS revenue
FROM retail.sales
WHERE sales_date >= DATE '2026-11-01'
  AND sales_date < DATE '2026-11-05'
GROUP BY store_id, category_id;
```

Look for full table scans caused by ineffective pruning, large
`Exchange` operators, sort or hash aggregation spills, uneven task
execution, and repeated scans or unnecessary materialization.

*Step 2: optimize scan volume.*

```python
sales = (
    spark.read.table("retail.sales")
    .where(
        (F.col("sales_date") >= "2026-11-01") &
        (F.col("sales_date") < "2026-11-05")
    )
    .select("store_id", "category_id", "net_amount")
)
```

This encourages partition and column pruning where the underlying
layout supports them.

*Step 3: use partial aggregation.* Spark generally inserts partial
aggregation automatically for supported aggregate functions:

```text
FileScan
  → Partial HashAggregate
  → Exchange
  → Final HashAggregate
```

The optimization benefit depends on the reduction ratio — if 10
billion input rows collapse into 1 million partial aggregate records,
the shuffle reduction can be substantial.

*Step 4: tune partition sizing based on measurements.*

```python
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.shuffle.partitions", "800")
```

The value `800` is only a test configuration, not a universal
recommendation. Compare alternative settings using input size per
task, shuffle partition sizes, spills, stage durations, and total
cost.

*Step 5: evaluate incremental aggregation.* If the same historical
data is repeatedly aggregated, the largest optimization may be to
avoid recomputing unchanged periods: maintain daily or hourly partial
aggregates and combine only affected periods. Incremental aggregation
must support corrections, deletions, and restatements — simply adding
new totals can produce incorrect results.

**Interviewer follow-ups**

- *Why might increasing partitions make the job slower?* Additional
  tasks increase scheduling, shuffle metadata, and output overhead.
- *Why might AQE not solve the entire problem?* AQE can optimize
  supported runtime plan decisions, but it cannot eliminate required
  computations or compensate for all data-layout and algorithmic
  inefficiencies.
- *What would you measure to prove success?* Runtime, bytes scanned,
  shuffle bytes, spill, CPU efficiency, output correctness, and total
  compute cost.

### Question 4 — Late-arriving retail transactions

**Interviewer:** Walmart needs five-minute store revenue aggregates.
Transactions can arrive up to two hours late, and some may arrive even
later. How would you design event-time processing without permanently
losing revenue?

**Model answer**

Separate low-latency provisional aggregates from historically correct
finalized aggregates. A watermark can control streaming state
retention, but it is not a universal guarantee that late events will
never arrive.

```python
from pyspark.sql import functions as F

windowed = (
    events
    .withWatermark("event_time", "2 hours")
    .groupBy(F.window("event_time", "5 minutes"), "store_id")
    .agg(
        F.sum("net_amount").alias("revenue"),
        F.count("*").alias("transactions"),
    )
)
```

For a watermark-aware aggregation, output mode affects when results
are emitted. Append mode generally emits finalized windows only after
the watermark permits finalization; update mode can emit changing
aggregates.

```text
StateStoreSave
  HashAggregate(final)
    Exchange hashpartitioning(window, store_id)
      HashAggregate(partial)
        EventTimeWatermark
          Streaming Source
```

State restoration and state-store operators appear in the actual
streaming physical plan.

*Production correctness strategy:*

1. Maintain event-time aggregates with a two-hour watermark policy.
2. Retain authoritative historical input for replay and corrections.
3. Identify records arriving outside the streaming correction horizon.
4. Recompute affected historical windows or apply controlled
   corrections.
5. Reconcile aggregate totals against authoritative transaction
   totals.

**Trade-off:** longer watermark delays increase the time for which
state may need to be retained; shorter delays reduce state pressure
but increase the need for correction processing.

**Interviewer follow-ups**

- *Does a two-hour watermark mean every event delayed by less than two
  hours is always accepted?* No. Acceptance depends on watermark
  progress and operator semantics, not solely the difference between
  arrival time and event time.
- *Can you guarantee correct revenue using only watermarks?* Not if
  arbitrarily late events must be included — you need a correction or
  reconciliation strategy.

### Question 5 — Incremental processing with corrections

**Interviewer:** A daily sales table contains 20 billion records. Only
0.5% change daily. The changes include inserts, updates, cancellations,
and historical corrections. How would you process these changes
efficiently while guaranteeing deterministic results?

**Model answer**

Use version-aware incremental processing. The core problem is not
merely identifying changed records — it is applying changes in the
correct order without allowing stale updates to overwrite newer state.

Example input:

| order_id | version | amount | operation |
| --- | --- | --- | --- |
| 101 | 1 | 500 | INSERT |
| 101 | 2 | 450 | UPDATE |
| 101 | 3 | 0 | DELETE |
| 102 | 1 | 700 | INSERT |

*Step 1: select latest changes per key.*

```python
from pyspark.sql import Window
from pyspark.sql import functions as F

w = Window.partitionBy("order_id").orderBy(F.col("version").desc())

latest = (
    changes
    .withColumn("rn", F.row_number().over(w))
    .where("rn = 1")
    .drop("rn")
)
```

This assumes versions are strictly ordered and unique per order. If
they are not, an additional authoritative tie-breaker is necessary.

*Step 2: apply version-aware changes.*

```sql
MERGE INTO retail.orders AS t
USING latest_changes AS s
ON t.order_id = s.order_id

WHEN MATCHED
  AND s.version > t.version
  AND s.operation = 'DELETE'
THEN DELETE

WHEN MATCHED
  AND s.version > t.version
  AND s.operation <> 'DELETE'
THEN UPDATE SET
  t.amount = s.amount,
  t.version = s.version

WHEN NOT MATCHED
  AND s.operation <> 'DELETE'
THEN INSERT (order_id, amount, version)
VALUES (s.order_id, s.amount, s.version);
```

**Critical production caveat:** if deleted records are physically
removed, a delayed older insert may later recreate them. To prevent
this, maintain a durable version/tombstone record or equivalent
authoritative ordering state even after a business record is deleted.

```text
Window(row_number)
  Sort(order_id, version DESC)
    Exchange hashpartitioning(order_id)
      Scan changes
```

The merge may then involve a join between source changes and target
data, followed by transactional file rewrites or other
storage-engine-specific operations.

**Interviewer follow-ups**

- *What if version 3 arrives before version 2?* Version-aware
  processing must reject the stale version 2 update.
- *Is `MERGE` automatically replay-safe?* No. Replay safety depends on
  source uniqueness, ordering, predicates, delete handling, and target
  state.

### Question 6 — Massive fact-to-dimension join

**Interviewer:** You must join 8 TB of transaction data with a 40 MB
product dimension. How would you optimize the join?

**Model answer**

A broadcast hash join is a strong candidate, assuming the dimension is
sufficiently small after filtering and projection and the join type is
supported.

```python
from pyspark.sql.functions import broadcast

result = transactions.join(broadcast(products), "product_id", "inner")
```

Expected physical plan:

```text
BroadcastHashJoin
  :- FileScan transactions
  +- BroadcastExchange
       +- FileScan products
```

The small dimension is distributed to executors, avoiding a large
shuffle of the transaction side.

**Trade-offs:** broadcast joins reduce shuffle cost but consume
executor memory — the dimension's serialized and in-memory
representation may be substantially larger than its compressed
on-disk size. If the dimension is too large or the join is
unsupported, a sort-merge join or another strategy may be preferable.

**Interviewer follow-ups**

- *What if the dimension grows to 5 GB?* Re-evaluate broadcast
  feasibility based on actual memory and execution metrics. Consider a
  shuffled join, filtering, or reducing the dimension before joining.
- *What if the fact table has a heavily skewed join key?* Investigate
  skew-aware join strategies, hot-key isolation, and salting where
  appropriate.

### Question 7 — Stateful processing at massive scale

**Interviewer:** Walmart wants to calculate the number of unique
active customers per store over a rolling 30-minute period. The system
receives millions of events per minute. How would you implement this
without unbounded state growth?

**Model answer**

First, clarify whether the business requires exact distinct counts or
allows approximate results.

*Exact approach:* maintain state keyed by store and customer, with
event-time information needed to expire activity correctly. A customer
contributes one to a store's active count while at least one
qualifying event remains within the rolling interval.

*Approximate approach:* use a sketch-based distinct-count algorithm,
such as HyperLogLog, where supported. However, rolling-window
expiration requires careful sketch design — a single cumulative
HyperLogLog sketch cannot simply remove expired customers.

| Approach | Accuracy | State cost |
| --- | --- | --- |
| Exact keyed state | Exact under defined event semantics | Potentially high |
| Approximate distinct sketches | Approximate | Often lower |
| Periodic batch recomputation | Exact or approximate | Higher query latency |
| Windowed sketch merging | Approximate | Depends on bucket count and overlap |

```text
Source
  → Event-time assignment
  → Keyed partitioning
  → Stateful update
  → State expiration
  → Aggregate output
```

**Interviewer follow-ups**

- *Why is `COUNT(DISTINCT customer_id)` expensive in streaming?* It
  can require substantial state to track unique identities across the
  relevant time horizon.
- *Can a watermark alone bound every type of state?* No. State cleanup
  depends on the operator and whether it has a finite time or
  key-retention condition.

### Question 8 — Failure recovery and deterministic replay

**Interviewer:** A distributed processing job handles 500 million
records. After writing 80% of its output, the driver crashes. The job
restarts and processes the same input again. How would you prevent
duplicate or inconsistent results?

**Model answer**

Distinguish between task retries, job retries, and externally visible
output commits. For a batch computation, the safest pattern is often
to compute a complete deterministic result and publish it atomically,
rather than exposing partially completed output.

*Example: partition-scoped replacement* — replay-safe when the same
logical input produces the same result and the storage transaction
commits atomically:

```python
(
    daily_result.write
    .format("delta")
    .mode("overwrite")
    .option("replaceWhere", "sales_date = '2026-11-04'")
    .saveAsTable("retail.daily_summary")
)
```

*Alternative: idempotent batch identifier* — for a compatible Delta
append workflow, use a stable transaction identifier and version to
deduplicate retries:

```python
(
    result.write
    .format("delta")
    .mode("append")
    .option("txnAppId", "daily-sales")
    .option("txnVersion", 20261104)
    .saveAsTable("retail.daily_sales")
)
```

The transaction identifier must be managed carefully, including
transaction retention, version reuse, and changes to processing logic.
This is not a universal exactly-once mechanism for every output
operation.

**Failure matrix**

| Failure point | Expected recovery strategy |
| --- | --- |
| Before processing | Retry input |
| During transformations | Recompute failed tasks |
| Before output commit | Retry output transaction |
| After commit, before acknowledgment | Detect committed transaction or perform idempotent retry |
| During external side effect | Use sink-specific idempotency or transactions |

**Interviewer follow-ups**

- *Is Spark checkpointing enough to guarantee exactly-once external
  writes?* No. Sink behavior and commit coordination matter.
- *Can deterministic processing still produce duplicates?* Yes.
  Deterministic results can be appended twice if output commits are
  not idempotent.

### Question 9 — Micro-batch processing under peak load

**Interviewer:** During a major retail promotion, event ingestion
increases from 100,000 to 500,000 records per second. A Spark
Structured Streaming query uses a 10-second trigger, but batches now
take 35 seconds. How would you restore processing stability?

**Model answer**

The system is experiencing a sustained processing-capacity deficit.
The 10-second trigger does not guarantee that batches finish within 10
seconds.

*Step 1: inspect progress.*

```python
progress = query.lastProgress
print(progress["batchDuration"])
print(progress["numInputRows"])
print(progress["inputRowsPerSecond"])
print(progress["processedRowsPerSecond"])
```

Also inspect per-source backlog, state operator metrics, and sink
duration.

*Step 2: identify the bottleneck.* Potential causes: insufficient
source partition parallelism, skewed aggregations, excessive shuffle,
state-store I/O, slow sink commits, insufficient compute capacity, or
large batches creating memory pressure.

*Step 3: apply targeted optimization.* If the problem is input volume
per batch, configure a source-specific rate limit where supported:

```python
stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "broker:9092")
    .option("subscribe", "sales")
    .option("maxOffsetsPerTrigger", 500000)
    .load()
)
```

This controls per-trigger intake; it does not increase sustainable
processing capacity. If arrivals continue to exceed processing
throughput, backlog will still grow.

*Step 4: improve sustainable throughput.* Optimize expensive
operators, reduce unnecessary state, improve partition balance, and
scale compute only where parallelism can be exploited.

*Step 5: validate recovery.* Measure how quickly backlog decreases
after traffic returns to normal. For example, if the system has
accumulated 100 million events and can process 200,000 events/sec more
than the current arrival rate, the idealized catch-up time is
100,000,000 ÷ 200,000 = 500 seconds — ignoring operational overhead
and changing rates.

**Interviewer follow-ups**

- *Would increasing the trigger interval to 60 seconds solve the
  issue?* Not necessarily. It may improve batching efficiency, but it
  cannot fix a fundamental capacity shortfall.
- *What if CPU utilization is only 30%?* Investigate I/O waits, skew,
  source partition limits, sink throughput, and state-store
  bottlenecks.

### Question 10 — Design a cost-efficient 100 TB/day processing platform

Principal architecture round.

**Interviewer:** Design a data processing platform that handles 100 TB
of data daily. Requirements: daily analytical aggregates must complete
within one hour; selected metrics require freshness within 30 seconds;
processing must support historical replay; late data and corrections
must be handled; the platform must tolerate worker failures; compute
cost must remain controlled.

**Model answer**

Use separate processing strategies for workloads with different
latency requirements while sharing deterministic business logic where
practical:

```text
Partitioned authoritative dataset (100 TB/day, historical retention)
  ├─ Batch / incremental       → large distributed aggregates  → daily aggregates (1-hour SLA)
  └─ Micro-batch / stream      → low-latency stateful operators → fresh metrics (30-second SLA)

Both paths feed deterministic replay and reconciliation
  → corrected and reconciled results
```

*Step 1: capacity planning.* 100 TB/day is approximately 1.16 GB/sec of
average logical input. Peak processing capacity must account for
burst traffic, compressed versus decoded data size, shuffle
amplification, and recovery headroom.

*Step 2: processing patterns.*

| Workload | Processing choice | Reason |
| --- | --- | --- |
| Daily historical aggregation | Distributed incremental batch | Efficient large-scale computation |
| Near-real-time metrics | Micro-batch or continuous streaming | Low freshness latency |
| Late corrections | Targeted incremental recomputation | Avoid full historical scans |
| Historical replay | Deterministic batch processing | Controlled reprocessing |
| Stateful metrics | Bounded keyed state | Correct event-time computation |

*Step 3: optimize distributed execution.* Use partition pruning,
column pruning, partial aggregation, efficient join strategies,
adaptive execution, and skew-aware processing. Avoid overpartitioning
physical storage and producing excessive small files.

*Step 4: reliability.* Use checkpointed state for streaming
computation, deterministic replay for historical computation, and
transactional or idempotent output publication.

*Step 5: cost optimization.* Track processing cost per TB, cost per
billion records, shuffle volume, CPU utilization, state storage cost,
and recovery overhead. A major cost-saving opportunity is reducing
unnecessary repeated processing, not simply selecting cheaper compute
instances.

*Step 6: validation.* Test peak-load throughput; p95/p99 processing
latency; worker failure recovery; replay correctness; duplicate and
out-of-order events; historical correction accuracy; and cost under
normal and peak loads.

**Interviewer follow-ups**

- *Would you use streaming for all 100 TB/day?* Not automatically —
  select the execution strategy based on freshness, state complexity,
  and cost.
- *What is the hardest correctness challenge?* Maintaining consistent
  business results across retries, late events, historical
  corrections, and multiple processing paths.
- *How do you demonstrate that the design meets the SLA?* Use
  production-representative load tests, failure injection, end-to-end
  latency measurements, and validated output invariants.
