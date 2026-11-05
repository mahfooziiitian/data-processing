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
level of depth, and a [second mock interview](#part-5-full-mock-interview-walmart-global-tech-principal-data-engineer-round-2)
covers ten further questions focused on correctness under duplication,
disorder, and historical correction; apply the same structure when
practicing the other companies.

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

## Part 5: Full mock interview — Walmart Global Tech, Principal Data Engineer (Round 2)

This is a second, independent mock interview at the same level as Part
4, built around correctness under duplication, disorder, and
historical correction rather than raw scale. As with Part 4, these are
**illustrative, company-styled practice scenarios**, not verified or
leaked questions from any company's actual interview process.

The lab setup below targets PySpark with Spark 4.x-style DataFrame
APIs and standard Spark SQL. A few exercises reference Delta Lake,
which requires a compatible Delta-enabled Spark runtime. Streaming
examples avoid `MemoryStream`-style test harnesses so the batch
reference calculations can be run and checked with ordinary files and
Spark Structured Streaming.

### Lab setup

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import (
    StructType, StructField, StringType,
    IntegerType, LongType, DoubleType,
    TimestampType,
)

spark = (
    SparkSession.builder
    .appName("Walmart-Principal-DE-Round2")
    .master("local[4]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("WARN")
```

For production, replace local execution with a properly sized
distributed cluster and validate the execution plan against your
runtime.

### Interview overview

| # | Scenario | Primary processing pattern |
| --- | --- | --- |
| 1 | Incremental sales with out-of-order corrections | Version-aware processing |
| 2 | Five-minute revenue with late transactions | Event-time windows |
| 3 | Watermark stalls during Black Friday | Watermark propagation |
| 4 | Exactly-once sales aggregation after crashes | Checkpoints and commits |
| 5 | Stateful customer deduplication | State retention and TTL |
| 6 | Streaming join between purchases and refunds | Stateful joins |
| 7 | Reprocess 30 days without double-counting | Deterministic replay |
| 8 | Incremental aggregates with historical corrections | Retractable aggregates |
| 9 | Recover a 500 GB stateful streaming job | State-store recovery |
| 10 | Design an enterprise-scale correctness-first processing engine | End-to-end correctness |

### Question 1 — Incremental sales with out-of-order corrections

Pattern: version-aware incremental processing.

**Interviewer:** A retail sales dataset contains 20 billion order
records. Each day, 100 million change records arrive. Changes may be
duplicated, delayed, or delivered out of order — for example, order
`O101` receives versions 1, 3, and 2, in that arrival order. Design an
incremental processor that maintains the latest correct state and
never lets an older version overwrite a newer one.

**Model answer**

The processing system must distinguish arrival order from
authoritative source order. The key invariant is:

\[
\text{storedVersion}(k) = \max(\text{acceptedSourceVersions}(k))
\]

assuming each version represents a complete replacement state for the
key.

*Step 1: create sample data.*

```python
changes = spark.createDataFrame(
    [
        ("O101", 1, 500.0, "UPSERT"),
        ("O101", 3, 450.0, "UPSERT"),
        ("O101", 2, 475.0, "UPSERT"),
        ("O102", 1, 700.0, "UPSERT"),
        ("O102", 2, 0.0, "DELETE"),
        ("O103", 1, 200.0, "UPSERT"),
        ("O103", 1, 200.0, "UPSERT"),
    ],
    ["order_id", "version", "amount", "operation"],
)
changes.createOrReplaceTempView("order_changes")
```

*Step 2: deterministically select the latest version.*

```sql
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY version DESC
        ) AS rn
    FROM order_changes
)
SELECT order_id, version, amount, operation
FROM ranked
WHERE rn = 1;
```

Expected result:

| order_id | version | amount | operation |
| --- | --- | --- | --- |
| O101 | 3 | 450 | UPSERT |
| O102 | 2 | 0 | DELETE |
| O103 | 1 | 200 | UPSERT |

This assumes identical duplicate versions carry identical content.
Conflicting records with the same version must be rejected or resolved
using an additional authoritative ordering field.

*Step 3: apply the latest state.*

```python
latest = spark.sql("""
    WITH ranked AS (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY order_id
                   ORDER BY version DESC
               ) rn
        FROM order_changes
    )
    SELECT order_id, version, amount, operation
    FROM ranked
    WHERE rn = 1
""")

active_orders = latest.filter(F.col("operation") != "DELETE")
active_orders.show()
```

Expected active orders:

| order_id | version | amount |
| --- | --- | --- |
| O101 | 3 | 450 |
| O103 | 1 | 200 |

**Production-grade state update.** A real incremental processor must
compare incoming versions against persisted versions from previous
runs, not only deduplicate the current batch. A robust target keeps
tombstones:

```sql
MERGE INTO order_state AS t
USING latest_changes AS s
ON t.order_id = s.order_id

WHEN MATCHED AND s.version > t.version
THEN UPDATE SET
    t.version = s.version,
    t.amount = s.amount,
    t.is_deleted = (s.operation = 'DELETE')

WHEN NOT MATCHED
THEN INSERT (
    order_id, version, amount, is_deleted
)
VALUES (
    s.order_id,
    s.version,
    s.amount,
    s.operation = 'DELETE'
);
```

This assumes a compatible table implementation supporting `MERGE`,
such as Delta Lake, and that `latest_changes` contains at most one
record per key. Keeping deletion markers prevents stale versions from
resurrecting deleted orders.

*Physical execution plan (current-batch dedup):*

```text
Window(row_number)
  Sort(order_id, version DESC)
    Exchange hashpartitioning(order_id)
      Scan changes
```

A target-state merge additionally requires matching source keys
against persisted target state and applying transactional updates.

**Failure matrix**

| Failure | Correct behavior |
| --- | --- |
| Version 3 arrives before version 2 | Version 2 rejected as stale |
| Same version arrives twice | No state change on replay |
| Delete version 5 followed by update version 4 | Order remains deleted |
| Crash before transaction commit | Retry safely |
| Crash after commit, before acknowledgment | Replay produces no additional change |

**Interviewer follow-ups**

- *Why is deduplicating only the current micro-batch insufficient?*
  An older version may arrive in a later batch. Correctness requires
  comparing against durable target state.
- *What happens if two events share the same version but different
  amounts?* The source ordering contract is ambiguous. Quarantine the
  conflict or use an authoritative tie-breaker; do not silently choose
  an arbitrary row.
- *When is version-based latest-state processing insufficient?* When
  changes are partial deltas rather than complete replacements, or
  when business logic requires preserving every intermediate
  transition.

### Question 2 — Five-minute revenue with late transactions

Pattern: event-time window aggregation.

**Interviewer:** Walmart needs revenue by store every five minutes.
Most transactions arrive within seconds, but some arrive 45 minutes
late and rare transactions arrive several hours late. The dashboard
must update quickly, while financial totals must eventually be
correct. How would you design the processing logic?

**Model answer**

I would separate two requirements: **freshness** — publish
provisional revenue promptly — and **correctness** — reconcile late
events and historical corrections against authoritative transaction
data. A watermark bounds state and governs event-time finalization,
but it cannot guarantee that no older events will arrive.

*Step 1: create sample events.*

```python
from datetime import datetime

events = spark.createDataFrame(
    [
        ("S01", "T1", datetime(2026, 11, 5, 10, 1), 100.0),
        ("S01", "T2", datetime(2026, 11, 5, 10, 3), 200.0),
        ("S01", "T3", datetime(2026, 11, 5, 10, 7), 300.0),
        ("S02", "T4", datetime(2026, 11, 5, 10, 4), 150.0),
    ],
    ["store_id", "transaction_id", "event_time", "amount"],
)
events.createOrReplaceTempView("sales_events")
```

*Step 2: batch reference calculation.*

```sql
SELECT
    store_id,
    window(event_time, '5 minutes') AS sales_window,
    SUM(amount) AS revenue,
    COUNT(*) AS transaction_count
FROM sales_events
GROUP BY
    store_id,
    window(event_time, '5 minutes');
```

Expected results:

| Store | Window (UTC) | Revenue | Count |
| --- | --- | --- | --- |
| S01 | 10:00–10:05 | 300 | 2 |
| S01 | 10:05–10:10 | 300 | 1 |
| S02 | 10:00–10:05 | 150 | 1 |

*Step 3: streaming implementation.* Assuming `streaming_events` is a
streaming DataFrame with the same schema:

```python
windowed = (
    streaming_events
    .withWatermark("event_time", "60 minutes")
    .groupBy(
        F.window("event_time", "5 minutes"),
        F.col("store_id"),
    )
    .agg(
        F.sum("amount").alias("revenue"),
        F.count("*").alias("transaction_count"),
    )
)
```

For provisional updates, use an output mode compatible with updating
aggregates and a sink that supports updates. For finalized append-only
output, the engine must wait until the watermark allows a window to
close.

*Physical execution plan:*

```text
StateStoreSave
  HashAggregate(final)
    Exchange hashpartitioning(store_id, window)
      HashAggregate(partial)
        EventTimeWatermark
          Streaming Source
```

Actual plans may also contain `StateStoreRestore`, projections, and
additional aggregation operators.

**Failure matrix**

| Scenario | Expected handling |
| --- | --- |
| Event arrives before watermark cutoff | Included under supported operator semantics |
| Event arrives after relevant state is finalized | Correct through separate reconciliation |
| Job crashes before checkpoint completion | Restore and replay as needed |
| Duplicate transaction arrives | Requires explicit deduplication |
| Dashboard displays provisional aggregate | Must allow later correction |

**Interviewer follow-ups**

- *Does `withWatermark("event_time", "60 minutes")` mean every event
  delayed less than 60 minutes is accepted?* No. The watermark depends
  on observed event-time progress; it is not a per-event arrival-time
  guarantee.
- *Why not use a 24-hour watermark?* It may increase state retention
  and delay finalization. Compare the late-arrival distribution with
  state cost and reconciliation requirements.
- *How do you handle a correction arriving three days later?*
  Recompute or adjust the affected historical window from authoritative
  data using a replay-safe correction process.

### Question 3 — Watermark stalls during Black Friday

Pattern: watermark progression, idle inputs, and state retention.

**Interviewer:** During Black Friday, Walmart processes transactions
from 10,000 stores. Some stores generate thousands of transactions per
second, while others remain inactive for several hours. A Spark
Structured Streaming aggregation uses a 30-minute watermark. After six
hours, state-store size increases dramatically, even though
transaction throughput remains stable. Explain the possible causes and
how you would troubleshoot them.

**Model answer**

The first hypothesis is that event-time progress is not advancing as
expected. However, inactive stores do not automatically stall Spark's
watermark: watermark progression is based on event-time observations
across the relevant streaming inputs, not on the minimum timestamp of
every individual store. I would distinguish three potential problems:

1. Watermark progression is stalled.
2. Watermark progression is healthy, but state cardinality is
   increasing.
3. The aggregation has no effective state-expiration condition.

*Step 1: inspect streaming progress.*

```python
progress = query.lastProgress
if progress:
    print("Watermark:", progress.get("eventTime"))
    print("State operators:", progress.get("stateOperators"))
    print("Input rows:", progress.get("numInputRows"))
```

Key metrics include `eventTime.watermark`, `eventTime.max`,
`numRowsTotal`, `numRowsUpdated`, `numRowsRemoved`, `memoryUsedBytes`,
and state-store commit/update timings, where exposed.

*Step 2: investigate multiple streaming inputs.* Spark uses a global
watermark for supported multi-input stateful queries. The default
multiple-watermark policy is generally `min`, which can hold back
progress when one input stream advances much more slowly.

```python
spark.conf.set(
    "spark.sql.streaming.multipleWatermarkPolicy",
    "min",
)
```

Changing this to `max` can improve progress but increases the risk of
dropping events from slower streams. I would not change the policy
without evaluating correctness.

*Step 3: check whether the state is bounded.*

```python
agg = (
    streaming_events
    .withWatermark("event_time", "30 minutes")
    .groupBy(
        F.window("event_time", "5 minutes"),
        "store_id",
    )
    .count()
)
```

A time-bounded window aggregation can remove finalized state when the
watermark advances sufficiently. By contrast, a running aggregation by
store without a time bound may retain state indefinitely.

*Physical execution plan:*

```text
StateStoreSave
  HashAggregate(window, store_id)
    Exchange hashpartitioning(window, store_id)
      HashAggregate
        EventTimeWatermark
          Streaming Source
```

The state-store operator's metrics are essential for determining
whether records are being removed.

**Failure and correctness matrix**

| Condition | Risk | Response |
| --- | --- | --- |
| No new events advance event time | Watermark stalls | Inspect source activity and progress |
| Slow input in a multi-input query | Global watermark delayed | Review input-specific progress |
| Unbounded keyed aggregation | Persistent state growth | Redesign state lifecycle |
| Watermark changed from `min` to `max` | Slow-stream data may be dropped | Validate late-data correctness |
| Job restarted with incompatible state configuration | Recovery failure or changed semantics | Use a controlled migration |

**Interviewer follow-ups**

- *Does a watermark advance based on wall-clock time?* No. Progress is
  driven by observed event timestamps and engine execution.
- *Can adding more executors fix watermark stalls?* Not necessarily.
  More compute cannot resolve a semantic lack of event-time progress.
- *Would you change the watermark delay from 30 minutes to five
  minutes?* Only if the business can tolerate the resulting late-data
  behavior or has a reliable correction process.

### Question 4 — Exactly-once sales aggregation after crashes

Pattern: checkpointing, transactional commits, and replay-safe output.

**Interviewer:** A Spark Structured Streaming job calculates revenue
every five minutes. During micro-batch 105, Spark reads 2 million
transactions, aggregation completes, and the output is written
successfully — but the driver crashes before Spark records successful
batch completion. After restart, Spark processes batch 105 again. How
do you guarantee that revenue is not counted twice?

**Model answer**

The critical distinction is between exactly-once internal processing
and exactly-once effects at the output. Spark may replay an
uncommitted micro-batch, so an output operation must tolerate repeated
execution. I would use a durable batch-commit ledger and transactional
aggregate updates.

*Step 1: understand the failure boundary.*

```text
Read batch 105 → calculate revenue → commit output
  → driver crashes before batch acknowledgment
  → batch 105 is replayed
```

*Step 2: define the correct commit protocol.* A transactional
relational sink could atomically execute the following logic:

```sql
BEGIN;

INSERT INTO processed_batches (
    application_id,
    batch_id
)
VALUES ('store-revenue-v1', 105)
ON CONFLICT DO NOTHING;

-- Apply aggregate deltas only if the batch ID
-- was newly inserted in this transaction.

COMMIT;
```

The ledger insert and aggregate update must occur in the same
database transaction — checking the ledger in one transaction and
updating revenue in another is not sufficient. For Delta Lake, a
suitable alternative is to write deterministic, versioned aggregate
snapshots or use supported transaction identifiers and carefully
designed idempotent writes.

*Step 3: PySpark `foreachBatch` structure.*

```python
def process_batch(batch_df, batch_id):
    partial = (
        batch_df
        .groupBy("store_id")
        .agg(F.sum("amount").alias("batch_revenue"))
    )
    # The implementation of this function must:
    # 1. Atomically claim (application_id, batch_id)
    # 2. Apply aggregate changes in the same transaction
    # 3. Treat a previously committed batch as a no-op
    transactional_commit(
        application_id="store-revenue-v1",
        batch_id=batch_id,
        data=partial,
    )
```

`transactional_commit` represents the required sink-specific
transaction implementation; it is not a built-in PySpark function. For
a runnable local demonstration of the replay decision:

```python
committed = set()
revenue = {}

def apply_batch(batch_id, updates):
    if batch_id in committed:
        return "ALREADY_COMMITTED"
    for store_id, amount in updates.items():
        revenue[store_id] = revenue.get(store_id, 0) + amount
    committed.add(batch_id)
    return "COMMITTED"

assert apply_batch(105, {"S01": 500}) == "COMMITTED"
assert apply_batch(105, {"S01": 500}) == "ALREADY_COMMITTED"
assert revenue["S01"] == 500
```

This is a single-process illustration only — the in-memory `set` is
not crash-safe; production needs durable atomic commits.

*Physical execution plan:*

```text
MicroBatchExecution
  HashAggregate(final)
    Exchange hashpartitioning(store_id)
      HashAggregate(partial)
        Streaming Source
```

`foreachBatch` invokes the user-defined sink processing for each
micro-batch; the sink transaction is outside Spark's physical query
plan.

**Failure matrix**

| Crash point | Correct recovery |
| --- | --- |
| Before input processing | Replay batch |
| During aggregation | Recompute batch |
| Before output commit | Retry transaction |
| After output commit, before Spark acknowledgment | Detect already-committed batch |
| During output transaction | Roll back or recover atomically |
| After checkpoint completion | Resume at subsequent batch |

**Interviewer follow-ups**

- *Is `foreachBatch` exactly-once by default?* No. It provides
  at-least-once batch execution behavior; exactly-once effects require
  additional sink guarantees.
- *Is a batch ID globally unique?* No. It must be scoped to a stable
  application/checkpoint identity — resetting a checkpoint can cause
  batch IDs to be reused.
- *Why is a separate commit ledger dangerous?* A crash between the
  ledger update and the business update can create either missing
  results or duplicate results.

### Question 5 — Stateful customer deduplication

Pattern: keyed state, deduplication, and bounded retention.

**Interviewer:** Walmart processes 800 million customer activity
events per day. Some events are duplicated because of upstream
retries. Each event has a unique `event_id`, and duplicates can arrive
up to 24 hours apart. Design an efficient deduplication processor.
Explain memory consumption, watermark behavior, and how you would test
correctness.

**Model answer**

I would first define whether the requirement is to deduplicate events
within a known time horizon, or to deduplicate every event ever
processed — these are fundamentally different state requirements. For
bounded deduplication, use event-time state and an expiration policy.

*Sample data.*

```python
from datetime import datetime

activity = spark.createDataFrame(
    [
        ("E101", "C1", datetime(2026, 11, 5, 10, 0)),
        ("E102", "C2", datetime(2026, 11, 5, 10, 1)),
        ("E101", "C1", datetime(2026, 11, 5, 10, 0)),
        ("E103", "C3", datetime(2026, 11, 5, 10, 2)),
    ],
    ["event_id", "customer_id", "event_time"],
)
activity.createOrReplaceTempView("activity")
```

*Batch reference.*

```sql
SELECT event_id, customer_id, event_time
FROM (
    SELECT *,
           ROW_NUMBER() OVER (
               PARTITION BY event_id
               ORDER BY event_time
           ) AS rn
    FROM activity
)
WHERE rn = 1;
```

*Streaming implementation.* For Spark versions supporting
watermark-aware within-watermark deduplication:

```python
deduplicated = (
    streaming_activity
    .withWatermark("event_time", "24 hours")
    .dropDuplicatesWithinWatermark(["event_id"])
)
```

This assumes duplicate records for an ID have event-time differences
within the configured bound — a 24-hour delay in arrival time is not
the same thing as a 24-hour difference in event timestamps.
`dropDuplicatesWithinWatermark` requires a supported Spark version,
and events outside its watermark semantics may be dropped or no longer
deduplicated as intended.

*State sizing.* Suppose 800 million unique event IDs must be retained
and each stored state entry costs an illustrative 100 bytes:

\[
800{,}000{,}000 \times 100 = 80\text{ GB}
\]

Actual state usage can be considerably different because of key
encoding, indexes, metadata, storage-engine overhead, and
checkpointing.

*Physical execution plan:*

```text
StreamingDeduplicateWithinWatermark
  EventTimeWatermark
    Streaming Source
```

State-store reads, writes, and recovery are handled by the streaming
execution engine.

**Failure matrix**

| Scenario | Expected behavior |
| --- | --- |
| Duplicate within supported retention horizon | Suppressed |
| Same event ID with conflicting payload | Requires explicit conflict policy |
| Duplicate after state expiration | May be treated as new |
| Restart with valid checkpoint | Restore deduplication state |
| Restart with new checkpoint | Previous deduplication state unavailable |
| Event timestamp is null or invalid | Validate or quarantine |

**Interviewer follow-ups**

- *Why not use `dropDuplicates(["event_id"])` without a watermark?*
  For an unbounded stream, it can require indefinitely growing
  deduplication state.
- *Can a Bloom filter guarantee exact deduplication?* No. Bloom
  filters can have false positives, which can incorrectly suppress
  valid events.
- *How would you guarantee permanent deduplication?* Use durable
  identity tracking with an explicitly defined retention and storage
  strategy — permanent exact deduplication generally requires
  persistent historical identity information.

### Question 6 — Streaming join between purchases and refunds

Pattern: stream-stream joins, event-time bounds, and state cleanup.

**Interviewer:** A customer purchases a product, then may request a
refund within seven days. Purchase and refund events arrive on
separate streams, and refund events may arrive before the
corresponding purchase event because of processing delays. Design a
streaming processor that matches purchases to refunds without losing
valid matches or allowing unlimited state growth.

**Model answer**

I would use a time-bounded stream-stream join where the business
contract defines the maximum refund interval. The main correctness
questions are: is the refund window based on purchase event time or
processing time? Can a purchase have multiple partial refunds? How
late can each stream arrive? What happens when a refund is unmatched
after the retention horizon?

*Step 1: create sample datasets.*

```python
from datetime import datetime

purchases = spark.createDataFrame(
    [
        ("O101", datetime(2026, 11, 1, 10, 0), 500.0),
        ("O102", datetime(2026, 11, 2, 12, 0), 700.0),
    ],
    ["order_id", "purchase_time", "purchase_amount"],
)
refunds = spark.createDataFrame(
    [
        ("R1", "O101", datetime(2026, 11, 3, 9, 0), 100.0),
        ("R2", "O102", datetime(2026, 11, 4, 8, 0), 700.0),
    ],
    ["refund_id", "order_id", "refund_time", "refund_amount"],
)
purchases.createOrReplaceTempView("purchases")
refunds.createOrReplaceTempView("refunds")
```

*Step 2: batch reference join.*

```sql
SELECT
    p.order_id,
    p.purchase_amount,
    r.refund_id,
    r.refund_amount
FROM purchases p
INNER JOIN refunds r
    ON p.order_id = r.order_id
   AND r.refund_time >= p.purchase_time
   AND r.refund_time <= p.purchase_time + INTERVAL 7 DAYS;
```

Expected output:

| order_id | purchase_amount | refund_id | refund_amount |
| --- | --- | --- | --- |
| O101 | 500 | R1 | 100 |
| O102 | 700 | R2 | 700 |

*Step 3: streaming implementation.*

```python
p = (
    purchase_stream
    .withWatermark("purchase_time", "2 hours")
    .alias("p")
)
r = (
    refund_stream
    .withWatermark("refund_time", "2 hours")
    .alias("r")
)
matched = p.join(
    r,
    F.expr("""
        p.order_id = r.order_id
        AND r.refund_time >= p.purchase_time
        AND r.refund_time <= p.purchase_time + INTERVAL 7 DAYS
    """),
    "inner",
)
```

This is a supported style of time-bounded stream-stream join. It
requires appropriately typed timestamp columns and compatible Spark
streaming configuration. The two-hour watermark delay is an assumption
about input disorder, not a replacement for the seven-day business
matching interval.

*Physical execution plan.* A representative plan is:

```text
StreamingSymmetricHashJoin
  Left:
    EventTimeWatermark
      Purchase Stream
  Right:
    EventTimeWatermark
      Refund Stream
  Join:
    order_id equality
    refund_time within purchase_time + 7 days
```

Spark maintains state for both sides until its event-time cleanup
conditions permit removal.

**Important production consideration.** A seven-day business interval
can result in substantial retained state — for example, at 100 million
purchases per day, the processor might need to retain hundreds of
millions of purchase-side records. I would compare a direct streaming
join against a design using durable keyed purchase state and
incremental refund matching. The alternative can be more economical,
but introduces different lookup, expiry, and recovery behavior.

**Failure matrix**

| Failure | Correct handling |
| --- | --- |
| Refund arrives before purchase | Retain refund until match or expiration |
| Duplicate refund ID | Deduplicate before applying financial effects |
| Partial refund | Preserve distinct refund events |
| Refund after seven-day business window | Apply defined exception policy |
| Watermark advances beyond matching horizon | State may expire |
| Worker crashes during join | Restore state and replay |

**Interviewer follow-ups**

- *Why do you need watermarks on both streams?* They provide
  event-time progress information used to bound state and determine
  when matching records are no longer expected.
- *Is a seven-day stateful join always a good design?* No. State size,
  checkpoint duration, latency, and source volume may make durable
  keyed lookup more appropriate.
- *How do you prevent duplicate refunds from double-counting revenue?*
  Deduplicate by a stable refund identifier and make downstream
  aggregate updates replay-safe.

### Question 7 — Reprocess 30 days without double-counting

Pattern: deterministic replay, historical backfill, and atomic
publication.

**Interviewer:** A bug in a revenue transformation caused incorrect
results for the last 30 days. The source contains 15 billion
transactions. You must recompute the affected aggregates while the
live processing system continues operating. How would you perform the
replay without duplicate results, missing corrections, or overwriting
newer data?

**Model answer**

I would treat historical replay as a versioned deterministic
computation. The fundamental invariant is:

\[
\text{Result} = f(\text{Input Snapshot}, \text{Logic Version})
\]

The same input snapshot and deterministic logic version should produce
the same logical output.

*Step 1: freeze the replay input.* Choose an authoritative input
snapshot or source version. Do not read a moving target while
attempting to compare historical results.

*Step 2: recompute affected aggregates.*

```python
from pyspark.sql import functions as F

replay_input = (
    spark.read.table("retail.transactions")
    .where(
        (F.col("sales_date") >= "2026-10-01")
        & (F.col("sales_date") <= "2026-10-30")
    )
)

recomputed = (
    replay_input
    .groupBy("sales_date", "store_id")
    .agg(
        F.sum("net_amount").alias("revenue"),
        F.count("*").alias("transaction_count"),
    )
)
```

This is runnable against an existing table with the stated schema. For
a versioned table, pin the read to the selected historical snapshot
rather than relying on the current table state.

*Step 3: write to isolated staging.*

```python
(
    recomputed.write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("retail.revenue_replay_staging")
)
```

*Step 4: validate before publishing.*

```sql
SELECT
    sales_date,
    COUNT(*) AS store_count,
    SUM(revenue) AS total_revenue
FROM retail.revenue_replay_staging
GROUP BY sales_date
ORDER BY sales_date;
```

Compare against independent expected totals and business invariants.

*Step 5: publish safely.* For a Delta target, a controlled
partition-scoped replacement can be used if the replay covers complete
target partitions.

```python
(
    recomputed.write
    .format("delta")
    .mode("overwrite")
    .option(
        "replaceWhere",
        "sales_date >= '2026-10-01' AND sales_date <= '2026-10-30'",
    )
    .saveAsTable("retail.daily_revenue")
)
```

This must be coordinated with live writers — atomic replacement of a
date range does not, by itself, prevent a stale replay from
overwriting newer corrections. A stronger publication design uses a
defined cutoff, compatible transaction isolation, and a catch-up or
reconciliation step for changes committed after the replay snapshot.

*Physical execution plan:*

```text
HashAggregate(final)
  Exchange hashpartitioning(sales_date, store_id)
    HashAggregate(partial)
      Filter(replay date range)
        FileScan
```

**Failure matrix**

| Failure | Correct behavior |
| --- | --- |
| Replay crashes before staging completes | Retry staging |
| Staging contains incomplete dates | Validation rejects publication |
| Live correction arrives during replay | Capture and reconcile after cutoff |
| Publication fails before commit | Original result remains |
| Replay publication succeeds, acknowledgment fails | Detect published version before retry |
| Same replay executed twice | Final result remains logically unchanged |

**Interviewer follow-ups**

- *Why not delete 30 days of data and reinsert everything?* That can
  expose incomplete results and complicate concurrent processing.
  Prefer transactional replacement or controlled version switching.
- *How do you handle a live correction arriving after the replay
  snapshot?* Use a change boundary and apply all subsequent changes
  after publishing the historical recomputation.
- *How do you verify that replay is correct?* Compare deterministic
  aggregates, uniqueness constraints, counts, and business invariants
  against an independent reference calculation.

### Question 8 — Incremental aggregates with historical corrections

Pattern: retractable aggregation and change-delta processing.

**Interviewer:** A customer buys a product for ₹1,000 on Monday. On
Tuesday, the amount is corrected to ₹900. On Wednesday, the
transaction is canceled. A daily revenue aggregation must remain
correct without recomputing all historical transactions. How would you
implement incremental aggregate maintenance?

**Model answer**

A simple append-only sum is incorrect when previously accepted values
can change — the processing system must calculate the difference
between old and new contributions:

\[
\Delta = \text{New Contribution} - \text{Old Contribution}
\]

For the example:

| Event | Previous | New | Revenue delta |
| --- | --- | --- | --- |
| Purchase | 0 | 1,000 | +1,000 |
| Correction | 1,000 | 900 | −100 |
| Cancellation | 900 | 0 | −900 |

Final contribution: ₹0.

*Step 1: implement a retractable aggregate.*

```python
from pyspark.sql import functions as F

changes = spark.createDataFrame(
    [
        ("O101", 1, 0.0, 1000.0),
        ("O101", 2, 1000.0, 900.0),
        ("O101", 3, 900.0, 0.0),
        ("O102", 1, 0.0, 500.0),
    ],
    ["order_id", "version", "old_amount", "new_amount"],
)
deltas = changes.withColumn(
    "revenue_delta",
    F.col("new_amount") - F.col("old_amount"),
)
deltas.show()
```

*Step 2: aggregate the deltas.*

```python
result = (
    deltas
    .groupBy("order_id")
    .agg(F.sum("revenue_delta").alias("net_contribution"))
)
result.show()
```

Expected:

| order_id | net_contribution |
| --- | --- |
| O101 | 0 |
| O102 | 500 |

*Spark SQL solution.* Register the DataFrame as `changes` before
running:

```python
changes.createOrReplaceTempView("changes")
```

```sql
WITH deltas AS (
    SELECT
        order_id,
        new_amount - old_amount AS revenue_delta
    FROM changes
)
SELECT
    order_id,
    SUM(revenue_delta) AS net_contribution
FROM deltas
GROUP BY order_id;
```

**Production correctness issue.** The example assumes `old_amount` is
accurate and each transition is applied exactly once. In real systems,
duplicate or out-of-order deltas can corrupt aggregates. A more robust
design stores the latest accepted version and contribution for each
order. For an incoming complete replacement event:

1. Compare its version with the persisted version.
2. Reject stale or duplicate versions.
3. Compute the difference between new and stored contributions.
4. Atomically update both the order state and aggregate contribution.

If an order changes its grouping dimensions, such as store or business
date, the old group must receive a negative adjustment and the new
group a positive adjustment.

*Physical execution plan:*

```text
HashAggregate(final)
  Exchange hashpartitioning(order_id)
    HashAggregate(partial)
      Project(new_amount - old_amount)
        Scan changes
```

**Failure matrix**

| Failure | Risk | Correct handling |
| --- | --- | --- |
| Correction replayed twice | Double subtraction | Version-aware idempotency |
| Cancellation before purchase | Incorrect intermediate total | Authoritative version ordering |
| Correction changes sales date | Wrong daily bucket | Retract old and add new contribution |
| Crash after state update but before aggregate update | Inconsistency | Atomic transaction or recoverable reconciliation |
| Missing old contribution | Incorrect delta | Read persisted prior state |

**Interviewer follow-ups**

- *Can you incrementally maintain `AVG`?* Yes. Maintain sum and count,
  then calculate sum/count, retracting both appropriately.
- *Can you incrementally maintain `MIN` or `MAX` using only the
  current minimum or maximum?* Not generally when deletions are
  allowed — removing the current minimum may require additional
  candidate state or recomputation.
- *Why are retractions important in streaming analytics?* Because
  updates, cancellations, and late corrections change previously
  published aggregate contributions.

### Question 9 — Recover a 500 GB stateful streaming job

Pattern: distributed state management, checkpoint recovery, and
rescaling.

**Interviewer:** A Walmart streaming application maintains
approximately 500 GB of state across 200 Spark tasks. During Black
Friday, several executors fail. The query restarts, but recovery takes
40 minutes, while the freshness SLA is 30 seconds. How would you
diagnose and redesign the stateful processing system?

**Model answer**

I would separate state correctness, recovery time, and steady-state
latency. A large state store does not automatically imply poor
performance, but its storage layout, checkpointing strategy, and
restoration behavior can become major bottlenecks.

*Step 1: inspect state metrics.*

```python
progress = query.lastProgress
if progress:
    for operator in progress.get("stateOperators", []):
        print("Operator:", operator.get("operatorName"))
        print("Rows:", operator.get("numRowsTotal"))
        print("Memory:", operator.get("memoryUsedBytes"))
        print("Custom metrics:", operator.get("customMetrics"))
```

Also inspect checkpoint duration and storage latency, the state-store
provider and configuration, state rows per partition, state size
distribution, RocksDB compaction and cache behavior (if applicable),
executor memory/local disk/network I/O, and time spent restoring state
versus replaying source data.

*Step 2: analyze state distribution.* Illustrative, hypothetical
per-partition state sizes for diagnostic purposes:

| Partition | State size |
| --- | --- |
| P1 | 4 GB |
| P2 | 5 GB |
| P3 | 18 GB |
| P4 | 6 GB |
| P5 | 5 GB |
| P6 | 4 GB |

A disproportionately large state partition (P3 above) can dominate
recovery time even when total state size is distributed across many
tasks. If one partition is substantially larger than others,
investigate key skew before changing infrastructure.

*Step 3: evaluate the state-store backend.* For compatible Spark
versions, a RocksDB-backed state store can be useful when state is too
large for efficient JVM heap management:

```python
spark.conf.set(
    "spark.sql.streaming.stateStore.providerClass",
    "org.apache.spark.sql.execution.streaming.state.RocksDBStateStoreProvider",
)
```

Set this before creating a new compatible stateful query. Changing a
state-store provider for an existing checkpoint is not a routine
in-place tuning operation — validate compatibility and use a supported
migration strategy, often involving a new checkpoint and controlled
state reconstruction.

*Step 4: reduce unnecessary state.* Review whether state expiration is
semantically valid, whether keyed state contains unnecessary columns,
whether state can be compacted or represented more efficiently,
whether hot keys create disproportionate state, whether the
aggregation can use bounded windows, and whether approximate
computation is acceptable for selected metrics.

*Step 5: evaluate recovery architecture.* For RocksDB-backed state,
incremental checkpointing may reduce checkpoint data movement under
supported configurations, although it does not eliminate all
restoration costs. Test recovery with production-sized state rather
than extrapolating from small development workloads.

*Physical execution plan:*

```text
StateStoreSave
  HashAggregate
    Exchange hashpartitioning(customer_id, N)
      HashAggregate
        Streaming Source
```

A representative stateful aggregation may also contain
`StateStoreRestore`. Changing state partition counts across checkpoint
recovery can have restrictions — rescaling must follow the framework's
supported state migration and recovery procedures.

**Failure matrix**

| Failure | Expected recovery |
| --- | --- |
| Executor process crashes | Restart affected tasks and restore state |
| Local RocksDB files lost | Restore from durable checkpoint state |
| Checkpoint files corrupted | Recovery may fail; use validated recovery procedures |
| Hot-key partition becomes oversized | Investigate key distribution and state design |
| State schema changes incompatibly | Controlled state migration |
| Source data no longer retained | Full recovery may be impossible |

**Interviewer follow-ups**

- *Does increasing executors automatically reduce the 500 GB state
  size?* No. It may improve resource availability, but existing state
  partitioning and recovery constraints remain.
- *Why might RocksDB outperform an in-memory state store?* It can
  manage large state outside the JVM heap and reduce heap pressure,
  although it introduces storage and compaction costs.
- *What is your recovery SLO?* I would define it explicitly, for
  example a recovery-time objective under five minutes, then validate
  it using failure injection and realistic state sizes.

### Question 10 — Design a Walmart-scale correctness-first processing engine

Final principal architecture round.

**Interviewer:** Design a data processing platform for a large retail
organization with the following requirements: five billion
transactions per day; 30-second freshness for operational revenue
dashboards; daily financial totals must be accurate after
reconciliation; transactions may be duplicated or arrive out of order;
historical corrections can arrive 30 days late; processing must
survive worker and driver failures; historical replay must not corrupt
live results; stateful computation must remain cost-efficient. Explain
the processing patterns, algorithms, Spark execution behavior, failure
recovery, and correctness guarantees.

**Model answer**

*Step 1: establish correctness invariants.* Before selecting the
execution strategy, define:

| Invariant | Requirement |
| --- | --- |
| Unique transaction identity | One accepted current state per transaction ID |
| Source ordering | Older versions cannot overwrite newer versions |
| Revenue correctness | Aggregates equal accepted transaction contributions |
| Replay safety | Reprocessing the same logical input does not change the final result |
| State recovery | Restart preserves the last committed logical state |
| Late correction | Historical results can be revised |
| Publication | Readers never observe partially committed aggregate results |

The most important invariant is:

\[
\text{Revenue}(d,s) = \sum_{\substack{t:\,\text{date}(t)=d \\ \text{store}(t)=s}} \text{AcceptedNetContribution}(t)
\]

This equation defines the business result independently of Spark,
state stores, or micro-batch execution.

*Step 2: choose processing patterns.*

```text
Authoritative transaction changes (event_id, transaction_id, source_version, event_time)
  → Incremental version-aware processing (deduplicate, reject stale versions, apply changes)
      ├─ Stateful streaming  → event-time windows, provisional aggregates (30-second freshness)
      └─ Incremental batch   → corrections, replay, reconciliation (final financial totals)
          → Versioned aggregate publication (replay-safe, corrected, validated results)
```

*Step 3: implement deterministic current-state processing.* A core
operation is to retain the newest source version for each transaction.

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window

def latest_transaction_state(changes):
    w = (
        Window.partitionBy("transaction_id")
        .orderBy(F.col("source_version").desc())
    )
    return (
        changes
        .withColumn("rn", F.row_number().over(w))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )
```

This function assumes one authoritative value per
`(transaction_id, source_version)`. Production input validation must
reject conflicting versions. For incremental execution, the result
must also be compared against durable current state.

*Step 4: maintain retractable aggregates.* Suppose an accepted
transaction changes from ₹1,000 to ₹800 — the correct adjustment is
−₹200, not an additional +₹800.

```python
def calculate_deltas(changes):
    return changes.withColumn(
        "amount_delta",
        F.col("new_amount") - F.col("old_amount"),
    )
```

The previous contribution must come from the authoritative accepted
state. If the store or business date changes, produce a negative
contribution for the old group and a positive contribution for the new
group.

*Step 5: define the physical execution plan* for store-level aggregate
updates:

```text
HashAggregate(final)
  Exchange hashpartitioning(store_id, sales_date)
    HashAggregate(partial)
      Project(amount_delta)
        Scan accepted changes
```

Evaluate this plan for partition skew, shuffle volume, aggregation
reduction ratio, state-store reads and writes, task spill, and output
commit duration.

*Step 6: define recovery boundaries.* Use durable checkpoints for
streaming state and transactional or idempotent publication for
aggregate results. For historical replay, pin an authoritative input
snapshot, recompute affected partitions, validate the results, and
publish through a controlled versioned process.

*Step 7: define observability.*

| Metric | Why it matters |
| --- | --- |
| Input records/sec | Processing demand |
| Processed records/sec | Sustainable capacity |
| p95/p99 processing latency | Freshness SLO |
| State rows and bytes | State growth |
| Watermark progress | Event-time finalization |
| Shuffle bytes and spills | Distributed execution efficiency |
| Checkpoint duration | Recovery overhead |
| Late corrections pending | Financial correctness |
| Replay mismatch count | Deterministic processing validation |

*Step 8: validate with chaos testing.* Test crashes before and after
output commits, duplicate events, out-of-order versions, late
corrections, state-store restoration, and concurrent historical
replay. The final acceptance criterion is not merely that the
processing job restarts — it is that the final business result
remains correct.

**Production failure matrix — final interview reference**

| Failure scenario | Main risk | Required guarantee |
| --- | --- | --- |
| Duplicate source event | Double counting | Stable-ID deduplication |
| Out-of-order update | Stale overwrite | Authoritative version ordering |
| Late event after watermark | Missing historical revenue | Reconciliation |
| Driver crash after output commit | Duplicate output | Idempotent commit |
| Worker crash during state update | Lost intermediate state | Checkpoint restoration |
| Checkpoint unavailable | Incomplete recovery | Retained source + state reconstruction plan |
| Historical replay overlaps live updates | Stale result publication | Version boundary and catch-up |
| Aggregate correction applied twice | Incorrect financial total | Atomic version-aware delta |
| Hot key during peak load | Excessive latency | Skew-aware processing |
| Unbounded state | Resource exhaustion | Explicit state lifecycle |

**Runnable correctness test lab.** The following local PySpark test
verifies several central properties from the interview. It does not
simulate distributed crashes or provide transactional sink guarantees,
but it establishes a deterministic reference for version-aware
processing.

```python
from pyspark.sql import SparkSession, functions as F
from pyspark.sql.window import Window

spark = (
    SparkSession.builder
    .master("local[4]")
    .appName("RetailProcessingCorrectness")
    .getOrCreate()
)

schema = """
    transaction_id STRING,
    source_version INT,
    store_id STRING,
    amount DOUBLE,
    is_deleted BOOLEAN
"""

changes = spark.createDataFrame(
    [
        ("T1", 1, "S1", 1000.0, False),
        ("T1", 3, "S1", 0.0, True),
        ("T1", 2, "S1", 900.0, False),
        ("T2", 1, "S1", 500.0, False),
        ("T2", 1, "S1", 500.0, False),
        ("T3", 1, "S2", 200.0, False),
    ],
    schema,
)

# Reject conflicting payloads for identical keys/versions.
conflicts = (
    changes
    .groupBy("transaction_id", "source_version")
    .agg(F.countDistinct("amount", "is_deleted").alias("distinct_payloads"))
    .filter(F.col("distinct_payloads") > 1)
)
assert conflicts.count() == 0

# Keep the newest accepted version per transaction (out-of-order versions).
w = Window.partitionBy("transaction_id").orderBy(F.col("source_version").desc())
latest = (
    changes
    .withColumn("rn", F.row_number().over(w))
    .filter(F.col("rn") == 1)
    .drop("rn")
)
assert latest.filter(F.col("transaction_id") == "T1").collect()[0]["source_version"] == 3
print("PASS: out-of-order versions")

# Duplicate events collapse to a single accepted row per key.
assert latest.filter(F.col("transaction_id") == "T2").count() == 1
print("PASS: duplicate events")

# Delete tombstones are preserved, not resurrected by an older version.
assert latest.filter(F.col("transaction_id") == "T1").collect()[0]["is_deleted"] is True
print("PASS: delete tombstones")

# Deterministic replay: recomputing from the same input yields the same result.
replayed = (
    changes
    .withColumn("rn", F.row_number().over(w))
    .filter(F.col("rn") == 1)
    .drop("rn")
)
assert sorted(latest.collect()) == sorted(replayed.collect())
print("PASS: deterministic replay")

# Aggregate correctness: deleted transactions contribute zero revenue.
revenue = (
    latest
    .filter(~F.col("is_deleted"))
    .groupBy("store_id")
    .agg(F.sum("amount").alias("revenue"))
)
assert revenue.filter(F.col("store_id") == "S1").collect()[0]["revenue"] == 500.0
print("PASS: aggregate correctness")
```

Expected output:

```text
PASS: out-of-order versions
PASS: duplicate events
PASS: delete tombstones
PASS: deterministic replay
PASS: aggregate correctness
```

For financial data, use an appropriate fixed-precision decimal type
rather than `DOUBLE`.

**What a Walmart Principal-level interviewer is evaluating.** At this
level, an interviewer expects you to explain not just how to implement
a Spark operation, but why its result remains correct under
duplication, disorder, retries, state expiration, and historical
replay. The strongest answers connect four layers:

1. **Business invariant** — what result must always remain correct?
2. **Processing algorithm** — how are changes, windows, and state
   computed?
3. **Distributed execution** — what shuffles, state stores, and
   bottlenecks arise?
4. **Failure boundary** — what happens if the process crashes
   immediately before or after a commit?

**Self-assessment scorecard.** Rate your confidence from 1 (basic) to
5 (can defend under challenging follow-ups):

| Area | Covers | Confidence (1–5) |
| --- | --- | --- |
| Incremental correctness | Versions, tombstones, retractions, stale-event handling | — |
| Event-time processing | Windows, watermark progression, late corrections | — |
| Stateful processing | State stores, TTL, bounded joins, recovery | — |
| Exactly-once effects | Replay, checkpoint boundaries, atomic commits | — |
| Production architecture | Scale, SLA, failure testing, cost and trade-offs | — |
