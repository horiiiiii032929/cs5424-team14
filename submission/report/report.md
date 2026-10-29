# 1. Team Contribution

The following contribution allocation is a draft for each member to confirm before submission.

| Person | Workload | Contribution |
| --- | --- | --- |
| Hikaru | A | Implemented a101-a115, correctness tooling, cluster evidence audits, figures and A analysis; assembled the submission draft. |
| Kelvin | A | Ran a102 and a10/a11/a12/a14; investigated write-path tuning and drafted the write-path analysis. |
| Dessi | B | Baseline installation and B b0-b6 design/results and B analysis; confirm individual attribution with the B pair. |
| Xincheng | B | B placement/index proposals and supplementary B experiments; confirm precise implementation, validation and writing contributions. |

# 2. Task 1: Baseline design for workload A

## `expt_a0`: baseline protocol and results


expt_a0 ran as Slurm job 918524 on five xcnf nodes, with xcnf8 as coordinator and four workers. It used PostgreSQL 18.6/Citus 14.1.0, scale 1, SERIALIZABLE isolation, 60-second warmup, 600-second measurements and full log sampling. The A transaction weights T1–T9 were 36/20/10/10/10/5/5/2/2 percent. Baseline work_mem was 32MB, shared_buffers 1GB and executor pool limit 4.

At 1/4/8/16/32/64 clients, baseline TPS was 3.220/2.283/2.285/2.368/2.405/2.283 respectively. p95 latency rose from 2654.656 ms at one client to 180370.276 ms at 64; p99 rose from 2698.524 to 187011.576 ms. pgbench exited zero in all six cases, but the last three had 25/51/50 serialization failures. Those failures must remain visible in comparisons.

At one client, T3 averaged 2678.797 ms, T4 458.862 ms and T7 51.114 ms. Weighting each transaction's observed mean latency by its completed count, T3/T4 accounted for about 93.6% of recorded time at one client and 97.2% at 64 clients. These are time shares, not workload weights. Throughput did not scale with more clients, so placement and the dominant reads take priority over short update transactions.

The baseline distributes orders and order_items by different generated IDs, and inventory by inventory_id. The relevant joins do not consistently match those keys. Fresh a0 control 977740 on xcnf0–4 completed 3.225/3.565/3.568/3.282/3.613/3.222 TPS at 1/4/8/16/32/64 clients, with 0/0/2/20/64/59 serialization failures. This is 41–56% above preserved baseline 918524 at 4+ clients; the cause is not established. Optimized a112 is compared against this fresh control on the same nodes.

| Clients | TPS | p50 ms | p95 ms | p99 ms | Serial. failures |
| --- | --- | --- | --- | --- | --- |
| 1 | 3.220 | 11.009 | 2654.656 | 2698.524 | 0 |
| 4 | 2.283 | 22.897 | 15398.450 | 18331.968 | 0 |
| 8 | 2.285 | 34.815 | 29532.561 | 32842.913 | 0 |
| 16 | 2.368 | 41.305 | 52999.831 | 58194.283 | 25 |
| 32 | 2.405 | 41.395 | 92368.465 | 100724.606 | 51 |
| 64 | 2.283 | 54.925 | 180370.276 | 187011.576 | 50 |

Table 2.1. Baseline A (job 918524), with latency percentiles in milliseconds. All measured exits are zero; the final three client counts retain serialization failures.

Source: `expt_a0/slurm-results/job-918524/benchmark-results/summary.csv`, `transaction_metrics.csv` and `config.txt` in the submitted result archive.

# 3. Task 2: Optimized design for workload A

The objective is average transaction throughput, with latency percentiles, retries and failures retained to assess the trade-offs. The main progression is a0 to a102 (lookup indexes), a111 (join-key colocation), and a112 (read-only declarations). a113, a114 and a115 test alternative follow-ups. Short diagnostics and cross-allocation comparisons are distinguished from the matched full a0/a112 matrix; the final combined improvement does not isolate each component's effect.

## `expt_a102`: lookup indexes

Kelvin's a102 job 965657 is independently verified from the raw files: all 12 source files match commit 82058e6 and the saved runtime hashes. It used xcnf1 coordinator/xcnf2–5 workers, PostgreSQL 18.6/Citus 14.1.0, scale 1 and the original benchmark settings. At 1/4/8/16/32/64 clients, TPS was 3.250/3.453/3.543/3.320/3.782/3.398, versus baseline 3.220/2.283/2.285/2.368/2.405/2.283.

All six measured a102 exits and measured serialization-failure counts are zero, with six passing core checks. Its 16-client warmup exited 2 and that case is excluded from clean comparisons. Clean concurrent cases show 49–57% gains over preserved a0 918524, but only approximately −3% to +6% against fresh a0 977740. Different node allocations and single observations prevent a matched index-only speedup claim. Source/raw evidence are in results/cluster-import-20261019/. Figure 3.1 retains the historical preserved-baseline comparison and flags the warmup abort.

![A figure](images/workload-a-baseline-indexes.pdf)

Figure 3.1. Verified baseline and lookup-index observations. The open point flags the aborted warmup; single runs do not estimate variability.

At one client, T7 mean latency falls from 51.114 to 13.709 ms, while T3/T4 remain 2668.472/454.362 ms. The indexes help individual operations but do not remove the dominant distributed-read cost.

## `expt_a101`: merchant colocation and failed diagnostics

a101 distributes merchant-owned data by merchant_id to make merchant-scoped operations local. Its small-fixture four-client cases aborted. In the cluster smoke suite, a101/job 977433 also aborted at four clients. The scale-1 diagnostic (job 977468) aborted in warmup and measurement, so its partial throughput is not ranked. These negative results motivated join-key rather than wholesale merchant colocation. The original slow post-run global-ID validator was replaced by equivalent exact checks; seven deliberate-corruption tests verified the replacement. Validation runs outside the timed interval.

## `expt_a111`: join-key colocation

a111 adapts the B team's placement ideas on top of a102: inventory is colocated with products by product_id, and order_items with orders by order_id; T7 uses the corresponding routing predicates. This targets the joins used by T3/T4 while retaining query semantics, SERIALIZABLE isolation, workload weights, durability and retry limits. a112 adds READ ONLY declarations to T3/T4/T6 relative to a111.

## `expt_a113`: safe-snapshot control against a111 and a112

a113 adds READ ONLY DEFERRABLE to a112's read transactions. The scale-1/four-client diagnostics used the original workload mix, 60-second warmups and 60-second measurements. All three completed both phases without measured failures or retries and passed exact validation.

| Experiment | Job | Change | TPS |
| --- | --- | --- | --- |
| `expt_a111` | 977617 | Join-key colocation on a102 | 89.917 |
| `expt_a112` | 977618 | a111 plus READ ONLY | 92.383 |
| `expt_a113` | 977619 | a112 plus DEFERRABLE | 90.550 |

Table 3.1. Diagnostic progression and safe-snapshot control. These single 60-second observations do not establish a reliable ranking or a general concurrency fix.

## `expt_a112`: matched full comparison and repeat

Full matched a0/a112 jobs 977740/977773 completed on xcnf0–4 with scale 1, six client counts, 60-second warmups and 600-second measurements. a112 delivered 54.2–90.8 TPS versus a0 3.2–3.6 TPS (16.8–28.2×), zero measured a112 failures and six passing validations. The baseline retains serialization failures. a112 is the recommended A design, subject to the A pair’s final confirmation.

At 1/4/8/16/32/64 clients, fresh a0 TPS was 3.225/3.565/3.568/3.282/3.613/3.222, and a112 was 54.238/85.042/87.378/88.073/90.660/90.788. TPS is completed scripts divided by 600 seconds, including expected business rollbacks. a112 retried 0/0/2/2/5/16 transactions; all retries succeeded. The unmodified a0 script has no post-run validation step.

At one client, T3 fell from 2656.9 to 6.8 ms and T4 from 454.5 to 1.5 ms. T6 remained about 257–263 ms. Count × mean latency gives T3+T4 93.5–97.7% of baseline time and T6 67–83% of a112 time; these are recorded time shares, not configured workload weights.

Repeat a112 job 978177 (seed 7) agreed within 2.5% in measured TPS. Its 64-client warmup exited 2 and that case is excluded from clean comparisons; all six measurements and validations passed. A worker’s commit-time serialization cancellation was wrapped as a generic Citus shard-commit error, so pgbench did not retry it. The general concurrency issue remains unresolved.

![A figure](images/workload-a-full-matched.pdf)

Figure 3.2. Matched full a0/a112 throughput and recorded time shares. The open diamond flags the seed-7/c64 warmup abort; that case is excluded from clean comparisons.

| Clients | TPS | p50 ms | p95 ms | p99 ms | Retried txns |
| --- | --- | --- | --- | --- | --- |
| 1 | 54.238 | 5.666 | 19.748 | 260.481 | 0 |
| 4 | 85.042 | 9.423 | 313.624 | 814.970 | 0 |
| 8 | 87.378 | 16.279 | 978.277 | 1531.221 | 2 |
| 16 | 88.073 | 23.309 | 2407.638 | 3101.652 | 2 |
| 32 | 90.660 | 38.125 | 623.002 | 6165.569 | 5 |
| 64 | 90.788 | 63.958 | 6597.911 | 10030.710 | 16 |


Table 3.2. Full a112 job 977773. All six warmup/measurement exits are zero and all measured failed-record counts are zero. A retry count is the number of retried transactions, not the number of final failures.

## `expt_a114`: maintained summaries as a negative result

a114 adds exact daily sales summaries to a112, with eight stripes per merchant/day to reduce write contention. At scale 1/four clients, job 979865 achieved 85.333 TPS and T6 mean latency 764.5 ms, compared with a112 diagnostic 92.383 TPS and T6 650.6 ms. Core and exact-summary checks passed, but this single observation provides no performance benefit and a114 is not recommended.

## `expt_a115`: timestamp-index control and reliability trade-off

a115 adds only orders(created_at) to a112 and retains its original T6 query. Diagnostic job 979866 achieved 288.633 TPS, T6 mean latency 115.9 ms, zero failed transactions and two retried transactions/two retry attempts, with passing validation. This isolates a useful timestamp-index hypothesis relative to a114's more complex summary design; a short diagnostic does not establish full-matrix reliability.

Full seed-42/seed-7 jobs 979909/979910 provide 12 client-count cases on xcnf0-4. Seven cases complete both phases: seed 42 at 1/4/8/16 clients (c4 has one final serialization failure) and seed 7 at 1/4/32. Six cases have zero failed records. Seed-42 c32/c64 and seed-7 c8/c16/c64 measurements exit 2; both c64 warmups exit 2. All 12 core validations pass and 26 runtime source-hash comparisons match. Passing integrity checks do not turn an aborted performance run into a clean comparison.

At one client both a115 seeds pass without failures at 115.485/109.893 TPS, versus same-seed a112’s 54.238/52.970 TPS (2.13×/2.07×). Eligible seed-42 c8/c16 and seed-7 c32 observations also support the index, but no clean repeated full matrix is established. The A pair must confirm the final selection before submission.

## Supporting implementations and validation scope

Local-only variants a103-a108 and a109/a110 explore one-call T1, maintained summaries, memory/executor settings and read-only declarations. Their source is retained under `supporting_implementations/local_only/` and their small-scale outputs under `evidence/local-only/`; they are not course-cluster benchmark experiments. The original distributed correctness suite passed 138 checks. Follow-up a109/a110 passed 26/38 checks and a111/a112/a113 passed 29 each (151 in total). Tests exercised actual read scripts, placement metadata and transfers with inventory IDs different from product IDs. Seven local four-client follow-up stress cases aborted; all 45 post-failure integrity checks passed. The local hot-merchant fixture differs from the full cluster dataset, so its timings are not ranked as cluster evidence.

## Write-path experimental method


Workload A is 75% writes by weight (T1 36%, T2 20%, T5 10%, T7 5%, T8 2%, T9 2%). In parallel with the placement work above, we tested whether the update path itself could be made cheaper: fewer round trips per update, HOT updates, less waiting for WAL flushes, and a fixed lock order for T7. Each experiment starts from `expt_a102` (job 965657), i.e. the baseline plus a102's three lookup indexes and its post-run correctness check (`sql/verify.sql`), and tests the changes described below. In particular, a11 uses a14 as its VACUUM/CHECKPOINT control. Workload mix, scale 1, SERIALIZABLE isolation, 60-second warmups, 600-second measurements and full log sampling are unchanged.

All runs were pinned to xcnf nodes. A first a12 submission that landed on xcnc nodes (job 967193) was cancelled and resubmitted (967217), since different hardware would confound a disk-sensitive setting. All four completed Slurm jobs exited 0 and passed all six post-run correctness checks; a10/c32 nevertheless has pgbench exit 2 and is excluded from clean comparisons. The invariant checks found no negative inventory, no duplicate order or order-item IDs, and every order total equal to the sum of its items.

To observe the update path directly, run.sh also snapshots `n_tup_upd`, `n_tup_hot_upd` and `n_tup_newpage_upd` from `pg_stat_user_tables` on every worker, for the shards of customers, products, inventory and orders, before and after each measured run, and writes the difference to `hot_updates.csv`. The snapshots run outside the 600-second window. In a10 this returned no rows, because Citus hides shard tables from catalog queries on workers; from a14 onwards the query first sets `citus.show_shards_for_app_name_prefixes = '*'`.

On this base, overall TPS is 3.0–3.8 for every variant. T3 and T4 still account for about 94% of recorded time and the four single-row updates about 0.2%, so the unchanged reads dominate overall throughput. That noise is visible in transactions none of these experiments touch: in the a10 run, T3, T4 and T6 were 9%, 14% and 9% slower at one client than in a102 (T3 2,911.7 vs 2,668.5 ms), and T4 was 53% slower at 16 clients. We therefore judge each change on the transactions it targets, and regard small throughput differences between these single runs as inconclusive; repeated matched runs are needed to estimate variability.

## `expt_a10`

T2, T5, T8 and T9 make up 34% of workload A. In the baseline each is already a single `UPDATE` (T2's stock check is already part of its `WHERE` clause), but each is wrapped in `BEGIN`/`COMMIT`. That costs three client-to-coordinator round trips instead of one, and adds a separate `COMMIT` at which Citus can turn a worker's serialization cancellation into the non-retryable shard-commit error shown in Figure 5.4.1.

### Key Changes

- Remove `BEGIN` and `COMMIT` from T2, T5, T8 and T9, so each `UPDATE` runs as one autocommit statement (Figure 3.10.1).
- The `UPDATE` text, its inputs and the SERIALIZABLE isolation level are unchanged.
| `UPDATE inventory` `SET quantity = quantity + (:inventory_change)::integer,` `    updated_at = CURRENT_TIMESTAMP` `WHERE inventory_id = (:product_id)::bigint` `  AND merchant_id = (:merchant_id)::bigint` `  AND product_id = (:product_id)::bigint` `  AND quantity + (:inventory_change)::integer >= 0;` |
| --- |

*Figure 3.10.1: T2 in expt_a10. expt_a102 runs the same statement between BEGIN; and COMMIT;*

### Benchmark Results and Analysis

| ** ** | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** |
| --- | --- | --- | --- |
| T2 | 0.63 → 0.62 | 11.74 → 6.73 | 54.93 → 47.58 |
| T5 | 0.40 → 0.39 | 11.95 → 6.71 | 90.53 → 54.55 |
| T8 | 0.08 → 0.08 | 15.17 → 9.18 | 58.92 → 64.23 |
| T9 | 0.07 → 0.07 | 13.46 → 5.90 | 450.3 → 118.2 |
| Overall | 3.40 → 3.35 | 77.88 → 68.68 | 129,160 → 128,928 |

*Table 3.10.1: Comparing expt_a10 against expt_a102 at 64 clients, on T2, T5, T8, T9 — single runs.*

| ** ** | **p50, 1 client (ms)** | **p50, 4 clients** | **p50, 8 clients** | **p50, 64 clients** |
| --- | --- | --- | --- | --- |
| T2 | 1.54 → 1.05 | 2.43 → 1.55 | 6.04 → 2.73 | 11.74 → 6.73 |
| T5 | 1.38 → 0.92 | 2.18 → 1.20 | 5.58 → 1.43 | 11.95 → 6.71 |
| T8 | 1.68 → 1.15 | 2.29 → 1.41 | 5.33 → 1.74 | 15.17 → 9.18 |
| T9 | 1.46 → 1.04 | 2.77 → 1.24 | 7.29 → 3.73 | 13.46 → 5.90 |

*Table 3.10.2: p50 latency of the targeted transactions, expt_a102 → expt_a10, at the client counts where both runs completed cleanly (a102's c16 warmup and a10's c32 measurement aborted). *

Median latency fell for all four transactions at every eligible client count, by 29% to 74%, and the gain grows with concurrency, consistent with shorter transactions holding row locks and coordinator connections for less time. p95 fell in 12 of 16 eligible cases; the exceptions are T2 and T5 at one client (within 0.13 ms) and T8 at 1 and 64 clients, which completed fewer than 50 transactions in each run. T2, T5, T8 and T9 recorded no failures, as in a102. Their TPS is unchanged because each is a fixed share of the mix, and overall TPS (3.03–3.79 vs 3.25–3.78) follows the slower unchanged reads in this run.

One pgbench client aborted early in the 32-client measurement with the shard-commit error. It was in T1 (script 0, command 153, which is T1's `COMMIT`), which a10 does not change, so the event is not attributed to a10, but the c32 run is excluded from comparisons. The same mechanism limits how much autocommit can help: in the a115 runs, 17 of 19 client aborts were T1 commits and only two were in T2/T9.

a10 helps the transactions it targets with no correctness cost, but it is not a throughput optimisation on this base. It remains a useful separately measured result; incorporation into a112 has not been benchmarked.

## `expt_a14`

The load inserts every row and then updates `orders.total_amount`, leaving dead tuples behind, and its dirty pages are still being flushed by checkpoints when measurement starts. a14 cleans both up before benchmarking. It also serves as the control for a11, which adds fillfactor on top of it.

### Key Changes

- At the end of every data load (before each client count), run `VACUUM (ANALYZE)` on each of the six tables, one command per table so that Citus propagates each one to the shards.
- Then run `CHECKPOINT` on all five nodes.

### Benchmark Results and Analysis

| ** ** | **HOT share of updates, without → with VACUUM** |
| --- | --- |
| inventory | 23.8–36.4% → 23.3–37.0% |
| orders | 75.5–81.2% → 76.2–81.5% |
| customers | 0–18.2% → 0–19.0% |
| products | 0–12.2% → 1.8–12.8% |

*Table 3.14.1: HOT share of updates per measured run (range over six client counts), expt_a12 (no VACUUM; its change does not affect HOT) → expt_a14. a102 recorded no HOT statistics.*

VACUUM made no measurable difference to the HOT share. orders was already about 80% HOT without it, likely because the load's update of `total_amount` leaves dead rows that page pruning reclaims. Overall TPS was −3.8% to +0.5% of a102. Write latencies moved in both directions (at 8 clients T9's p50 fell from 7.29 to 3.66 ms while T8's rose from 5.33 to 7.23 ms), and one serialization failure was recorded at 32 clients. a14 has no measurable effect, and we drop it.

## `expt_a11`

When PostgreSQL updates a row it writes a new row version. If the page has free space and no indexed column changes, this is a HOT (heap-only tuple) update: the new version stays on the same page and no index entries are added. Otherwise the new version goes to another page and every index on the table gets a new entry. Tables are loaded with full pages (fillfactor 100), so most inventory updates in a14 moved to a new page. Leaving 20% free space on each page should make them HOT.

### Key Changes

- Create customers, products, inventory and orders `WITH (fillfactor = 80)`. a11's schema log confirms `fillfactor=80` on the shards of all four tables.
- Keep a14's VACUUM and CHECKPOINT after every load, so a11 differs from a14 only in fillfactor.
- No index covers an updated column (`quantity`, `order_status`, `email`, `price`), so every update stays HOT-eligible.

### Benchmark Results and Analysis

| ** ** | **HOT share of updates** | **Updates moved to a new page, per run** |
| --- | --- | --- |
| inventory | 23.3–37.0% → 100% | 1,751–2,197 → 0 |
| orders | 76.2–81.5% → 100% | 181–218 → 0 |
| customers | 0–19.0% → 100% | 20–43 → 0 |
| products | 1.8–12.8% → 100% | 32–54 → 0 |

*Table 3.11.1: HOT updates per measured run, expt_a14 → expt_a11 (range over six client counts).*

| ** ** | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** |
| --- | --- | --- | --- |
| T2 | 0.64 → 0.63 | 1.48 → 1.59 | 9.17 → 2.31 |
| T5 | 0.35 → 0.35 | 1.37 → 1.34 | 13.02 → 2.11 |
| T6 | 0.16 → 0.15 | 266.4 → 280.7 | 277.8 → 292.3 |
| Overall | 3.23 → 3.19 | 11.30 → 11.31 | 2,670 → 2,667 |

*Table 3.11.2: Comparing expt_a11 against expt_a14 at 1 client, where contention does not mask per-statement cost.*

Every update in a11 was HOT, at every client count, and none moved to a new page; fillfactor alone produced this. Even so, neither overall TPS (−2.4% to +1.1% of a102) nor write latency changed consistently. The update rate explains why: inventory received only about 2,500–3,100 updates per 10-minute run, roughly 4–5 per second across four workers, so the index maintenance saved is negligible. The cost shows in the scan: T6 at one client took 280.7 ms (p50) against 266.4 ms in a14, consistent with orders occupying up to 25% more pages.

a11 recorded zero retried transactions at every client count, whereas a102, a10, a14 and a12 recorded 23–26 each, mostly at 16+ clients. A plausible mechanism is that HOT updates insert no index entries, leaving SERIALIZABLE fewer index-page read/write conflicts to track. This is one run with small counts and needs a repeat before it can be claimed.

The mechanism works but does not pay off at a102's update rate. It is worth revisiting on a112, which completes about 20 times more transactions per second.

## `expt_a12`

By default every commit waits until its WAL record is flushed to disk on each node it wrote to. T1 and T7 write to several shards and commit with two-phase commit, so they wait for several flushes. With `synchronous_commit = off` the commit returns before the flush.

### Key Changes

- Set `synchronous_commit = off` in `postgresql.conf` on the coordinator and all four workers (written by `init_node`).
- Leave `shared_buffers` (1 GB), `max_wal_size` (16 GB) and `checkpoint_timeout` (30 min) unchanged: no "checkpoints are occurring too frequently" warnings appeared, and each worker's data (estimated under 1 GB) already fits in the buffer pool. The memory a job can use is capped by Slurm's cgroup limit (3,072 MB per CPU × 4 CPUs = 12 GB per node), not by the node's RAM. `synchronous_commit = local` was not tested because without standbys it behaves the same as `on`.

### Benchmark Results and Analysis

| ** ** | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** |
| --- | --- | --- | --- |
| T1 | 1.33 → 1.34 | 44.86 → 41.98 | 87.27 → 89.38 |
| T2 | 0.71 → 0.72 | 6.04 → 4.61 | 19.91 → 16.99 |
| T5 | 0.35 → 0.36 | 5.58 → 4.13 | 20.84 → 15.80 |
| T8 | 0.05 → 0.05 | 5.33 → 2.54 | 14.40 → 12.11 |
| T9 | 0.06 → 0.06 | 7.29 → 3.57 | 20.11 → 17.71 |
| Overall | 3.54 → 3.59 | 41.88 → 39.56 | 19,514 → 19,627 |

*Table 3.12.1: Comparing expt_a12 against expt_a102 at 8 clients, on the write transactions — single runs.*

Single-shard updates look faster at 8 clients, but a14, which does not change commit behaviour, shows similar drops at the same client count (p50 T2 4.76, T5 3.85, T9 3.66 ms), so these cannot be attributed to a12. T1, the transaction that waits for the most flushes, did not improve (one-client p50 11.68 → 11.86 ms), and overall TPS was −0.4% to +3.5% of a102. T1's latency is therefore dominated by its many client round trips rather than by WAL flushes, which supports the one-call T1 approach in a103.

The durability cost is real. With `synchronous_commit = off`, a commit is acknowledged before its WAL reaches disk, so a crash of any node can lose roughly the last 0.6 seconds (three times `wal_writer_delay`) of transactions that clients were told had committed. The database stays consistent, but those orders and stock changes disappear. Because T1 and T7 commit across shards with two-phase commit, a worker crash could also lose that worker's part of a transaction the coordinator reported as committed. For an order-processing system this is not acceptable for no measurable gain, and we drop a12.

## Unrun T7 rewrite proposal (a13)

a13 planned to rewrite T7 so that it locks its two inventory rows in a fixed order, to prevent deadlocks. The evidence removed its premise. The preserved baseline (918524) recorded zero deadlock failures; all 126 failed transactions at 16/32/64 clients were T7 serialization failures ("could not serialize access due to read/write dependencies"). T7 looked up its rows by `product_id` while inventory was distributed by `inventory_id`, so each lookup scanned every inventory shard, and under SERIALIZABLE those scans conflicted with concurrent T1/T2 writes. a102's `inventory(product_id)` index removed those scans: T7's failures fell to zero and its one-client latency fell from 51.1 to 13.7 ms. a112 goes further by distributing inventory by `product_id` (similar to expt_b1), so a lock-order rewrite had nothing left to fix.

## Write-path summary

On the a102 base, write-path tuning cannot move overall throughput while distributed reads take about 94% of recorded time. a10's autocommit is the one change with a clear, consistent benefit for its own transactions (29–74% lower median latency at every eligible client count) and is retained as a separately measured result. A combined a10/a112 design has not been benchmarked. a11 shows the HOT mechanism working (100% HOT updates) but needs a higher update rate to matter. a12 trades durability for no measurable gain, and a14 has no effect. Two lessons carry into the rest of this section: identical code varied by 9–14% in mean latency between single runs at one client, and more under contention, so smaller differences need repeats on matched nodes; and the client aborts that limit our fastest designs come mainly from T1's commit, not from the single-statement updates.


# 4. Task 3: Baseline design for Workload B

Workload B is made up of the same 9 transactions but with a different weight mix. Most notably, 80% of the transactions involve writing data (T1, T2, T5, T7, T8, T9). T7 itself occupies the largest proportion at 30%, 3 times higher than the next most frequent transaction.

Evidence review — 22 October: b0–b6 scripts and raw outputs are archived from branch commit 5fa38157a7c1cb9abf1097e731f934a97a3db7c4. All 42 cases have been checked for phase exits and transaction-log counts. Every 64-client B case has an aborted warmup or measurement; those values below are diagnostic observations, excluded from clean performance comparisons. Node allocations vary; no matched full-series speedup is established.

| **Txn** | **Name** | **Weight** | **Description** |
| --- | --- | --- | --- |
| T1 | Place Order | 10% | Place a pending order for the customer, decrement the stock count, and insert the order items. Rollback if customer or product is missing, or there isn’t sufficient stock. |
| T2 | Update Inventory | 10% | Adds a random delta to a single product’s stock. Skip if the stock count becomes < 0. |
| T3 | Customer Order History | 5% | Retrieve 20 most recent orders and the order items. |
| T4 | Product Lookup | 5% | Retrieve information on a single product and its inventory quantity. |
| T5 | Update Order Status | 10% | Update a random order’s status. |
| T6 | Global Sales | 10% | Aggregate sales metrics for all merchants and get the top 20. |
| T7 | Inventory Transfer | 30% | Moves stock between two random products. |
| T8 | Update Customer | 10% | Updates a single customer’s email |
| T9 | Update Product | 10% | Updates the price of a single product |

*Table 4.1.1 Transaction types and weights for workload B*

## Experiment setup

Every benchmark experiment runs as a single Slurm job on NUS SoC compute cluster. The job deploys a 5-node Citus PostgreSQL distributed database, with a single coordinator and 4 workers. `pgbench` runs on the coordinator node and connects only to the coordinator, such that every statement passes through it.

- The software versions are Citus `14.1.0` on PostgreSQL `18.6`.
The default settings used for the benchmarking are:

- `shared_buffers` 1 GB
- `work_mem` 32 MB
- `max_connections` 1000,
- `SERIALIZABLE` isolation
- repartition joins enabled
- `citus.max_adaptive_executor_pool_size` 4
- `citus.max_shared_pool_size` 300

## `expt_b0`

| **Clients** | **TPS** | **p50 (ms)** | **p95 (ms)** | **p99 (ms)** | **Txn  retried** | **Serial. failures** | **Exit code** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3.77 | 14 | 666 | 4,013 | 0 | 0 | 0 |
| 4 | 3.46 | 44 | 12,917 | 17,040 | 77 | 10 | 0 |
| 8 | 3.64 | 59 | 6,736 | 31,323 | 245 | 101 | 2 |
| 16 | 3.54 | 36 | 25,595 | 53,878 | 468 | 267 | 2 |
| 32 | 3.17 | 32 | 75,582 | 90,242 | 490 | 340 | 0 |
| 64 | 3.19 | 35 | 133,192 | 160,032 | 633 | 493 | 0 |

*Table 4.2.1 expt_b0 latencies and transaction throughput (c8/c16 measured abort; c64 warmup abort; failures retained).*

| **Txn** | **Avg latency, 1 client (ms)** | **Share of time, 1 client** | **Avg latency, 64 clients (ms)** | **Share of time, 64 clients** |
| --- | --- | --- | --- | --- |
| T3 | 4,037 | 67.6% | 145,216 | 58.8% |
| T6 | 399 | 15.1% | 7,664 | 5.7% |
| T4 | 633 | 9.5% | 69,987 | 30.3% |
| T7 | 66 | 7.2% | 5,655 | 5.1% |
| T1 | 11 | 0.4% | 165 | 0.1% |
| T2, T5, T8, T9 | 1.4 to 1.6 each | 0.1% each | 15 to 33 each | under 0.1% each |

*Table 4.2.2 expt_b0 latencies and share of total time per transaction (64-client values are flagged diagnostic observations). *

The baseline’s raw summaries show about 3.2–3.8 TPS. c8/c16 measurements and c64 warmup aborted; phase-complete c4/c32 still record 10/340 serialization failures. Only c1 has both phases complete and zero measured failures. The latency/time-share observations motivate T3/T4 placement work, but the c64 figures are flagged diagnostic evidence rather than a clean baseline.

# 5. Task 4: Optimized design for Workload B

As suggested in the project description, the sequence of optimizations was progressively conducted. In general, each optimization was selected based on the measurements of the previous experiment, we selected the optimizations based on the workload weights and the performance bottlenecks observed in previous experiments.. Within the allowed tuning scope we changed the data distribution, the schema, the indexes and the transaction code.

## `expt_b1`

T7 makes up 30% of workload B, and based on the vanilla baseline schema, each of its four `SELECT` queries will scan all 32 shards of `inventory` because they filter on `product_id`. In addition, T4 requires a repartition join between `products` and `inventory` on `product_id`. Distributing `inventory` on `product_id`, in the same co-location group as `products`, optimises both. The expected outcome is every T7 `SELECT` routes to one shard, and the T4 join becomes local to one shard.

### Key Changes

1. Change the definition of `inventory`  so the primary key becomes `(product_id, inventory_id)`;
2. `inventory` to be distributed on `product_id` and `colocate_with => 'products'`.
3. T7’s two updates retain the selected inventory IDs and add their selected product IDs as routing predicates. The supplied fixture happens to use inventory_id equal to product_id, but the SQL looks up actual inventory IDs and does not rely on that equality.

### Benchmark Results and Analysis

|  | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** | **p99 Latency (ms)** |
| --- | --- | --- | --- | --- |
| T7 | 0.44 → 0.73 | 1,517 → 275 | 17,736 → 2,164 | 26,139 → 3,465 |
| T4 | 0.21 → 0.12 | 74,221 → 53 | 84,350 → 216 | 87,024 → 381 |
| Overall | 3.19 → 2.26 | 35 → 249 | 133,192 → 18,335 | 160,032 → 926,499 |

*Table 5.1.1: Comparing expt_b1 against expt_b0 at 64 clients, on T4, T7 — flagged raw observations; aborted phases exclude a clean comparison.*

The flagged c64 observations show lower T7/T4 latencies and fewer recorded serialization failures, consistent with the routing hypothesis. Both b0 and b1 c64 warmups aborted, and their allocations differ (xcnf versus xcnc); these ratios do not establish a clean matched causal effect.

The raw c64 throughput falls from 3.19 to 2.26 TPS, but aborted warmups and different hardware prevent a clean comparison. T3 remains a candidate bottleneck in the recorded time shares.

A T7-only supplementary comparison uses `expt_b201` (originally expt_xc_b1, job 989344) and baseline `expt_b0`/job 988876. At one client, the recorded throughput is 5.188 versus 334.518 TPS and mean latency is 192.786 versus 2.984 ms. The baseline uses xcnc34-38 while the optimized run uses xcnf10-14, so the full difference cannot be attributed to the routing change alone. T7 is 100% of this supplementary workload; these observations do not replace the original B mix.

## `expt_b2`

T3 has accounted for most of the time during the benchmarking runs up till this point. Its join of `orders` and `order_items` on `order_id` was a repartition join and required shifting rows to different workers as `order_items` was distributed on `order_item_id` rather than `order_id`.

### Key Changes

1. Change the primary key of `order_items` to be `(order_id, order_item_id)`.
2. `order_items` is distributed on `order_id`  and is co-located with `orders` via `colocate_with => 'orders'`.

### Benchmark Results

|  | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** | **p99 Latency (ms)** |
| --- | --- | --- | --- | --- |
| T3 | 0.11 → 2.37 | 885,875 → 1,381 | 941,152 → 2,139 | 956,702 → 2,422 |
| T6 | 0.20 → 4.61 | 15,967 → 12,443 | 17,829 → 13,782 | 18,483 → 14,275 |
| Overall | 2.26 → 46.04 | 249 → 68 | 18,335 → 12,444 | 926,499 → 13,510 |

*Table 5.2.1: Comparing expt_b2 against expt_b1 on T3, T6 at 64 clients — flagged raw observations; aborted phases exclude a clean comparison.*

The c64 raw observations suggest much lower T3 latency after order/item colocation, but b1’s warmup and b2’s measurement aborted. The apparent 20-fold TPS ratio is diagnostic, not an eligible matched speedup. b2 has complete zero-failure phases at 1/4/8/16 clients.

| **Txn** | **Avg latency, 1 client (ms)** | **Share of time, 1 client** | **Avg latency, 64 clients** | **Share of time, 64 clients** |
| --- | --- | --- | --- | --- |
| T3 | 10.9 | 1.7% | 1,418 | 5.3% |
| T6 | 265 | 87.0% | 12,405 | 89.6% |
| T4 | 1.5 | 0.3% | 29 | 0.1% |
| T7 | 5.2 | 5.2% | 106 | 2.3% |
| T1 | 11.3 | 3.8% | 237 | 1.7% |
| T2, T5, T8, T9 | 1.4 to 1.5 each | 0.5% each | 32 to 36 each | 0.2 to 0.3% each |

*Table 5.2.2: expt_b2 latencies and share of total time per transaction (64-client values are flagged diagnostic observations).*

Looking at the proportion of time spent on each transaction type, T6 now became the highest, at about 90% of all time.

## `expt_b3`

T6 aggregates, per merchant, the total number of orders and revenue amount in the last 30 days (via `created_at` column), and returns the top 20. Under the vanilla baseline definition, there is no index on `created_at`, hence Postgres needs to perform sequential table scan.

Postgres stores a table in 8KB pages, each holding the data tuples. When it needs a row, it reads the entire page, so the cost of a query is mostly the number of pages it reads. From `run.sh`, orders timestamp are generated in the following fashion:

`created_at` `= current_timestamp - (id * 31) mod 365 days`

and every page contains rows throughout the year. An ordinary B-Tree index can quickly list all the rows in the last 30 days, but it stores only the indexed column, and not the other information that T6 requires. To get those, Postgres still has to read the rows, which means reading all the pages of the table.

### Key Changes

1. Create a covering index, `orders(created_at) INCLUDE (merchant_id, total_amount)` that is sorted by date, and each entry carries the other two columns T6 needs. Postgres will only need to perform an index-only scan to retrieve all the data required by T6.
2. Perform `VACUUM` to mark table pages all-visible in the visibility map, enabling index-only scans to skip the table.

### Benchmark Results and Analysis

|  | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** | **p99 Latency (ms)** |
| --- | --- | --- | --- | --- |
| T6 | 4.61 → 24.48 | 12,443 → 1,213 | 13,782 → 1,725 | 14,275 → 2,038 |
| T3 | 2.37 → 12.52 | 1,381 → 607 | 2,139 → 1,294 | 2,422 → 2,109 |
| Overall | 46.04 → 249.24 | 68 → 35 | 12,444 → 1,231 | 13,510 → 1,619 |

*Table 5.3.1: Comparing expt_b3 against expt_b2 on T3, T6 at 64 clients — flagged raw observations; aborted phases exclude a clean comparison.*

b3’s c1 phases complete at 97.932 TPS with no measured failures. c4–c64 measurements abort, and c8–c64 warmups also abort. Their raw latency/TPS improvements are retained as diagnostic observations; the c64 5-fold ratio does not establish clean performance gain.

## `expt_b4`

The saved logs show worker serialization cancellations and Citus shard-commit errors that pgbench treats as client aborts (Figure 5.4.1). b4 tests READ ONLY together with coordinator-resolved T6 timestamps and plan capture; its node allocation also differs from b3. The resulting reduction in aborts is an observation, not an isolated READ ONLY causal test or a general concurrency fix.

| `WARNING:  failed to commit transaction on xcnf11:5446` `pgbench: error: client 2 script 0 aborted in command 153 query 0: ERROR:  could not commit transaction for shard 102081 on at least one active node` |
| --- |

*Figure 5.4.1: Log snippets of serialization error*

### Key Changes

1. T3, T4 and T6 begin with `BEGIN READ ONLY` instead of `BEGIN`.
2. T6 reads the current time once on the coordinator (`LOCALTIMESTAMP`) and passes the window to its query as two literal timestamps.
3. `run.sh` saves `EXPLAIN (ANALYZE, VERBOSE, BUFFERS)` output for T6, T3 and T5.

### Benchmark Results and Analysis

|  | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** | **p99 Latency (ms)** |
| --- | --- | --- | --- | --- |
| T6 | 24.48 → 31.17 | 1,213 → 1,242 | 1,725 → 1,758 | 2,038 → 2,075 |
| Overall | 249.24 → 316.00 | 35 → 37 | 1,231 → 1,242 | 1,619 → 1,656 |

*Table 5.4.1: Comparing expt_b4 against expt_b3 on T6 at 64 clients — flagged raw observations; aborted phases exclude a clean comparison.*

Measured client-abort messages total 41 in b3 and two in b4; b4 still exits 2 at c32/c64. b4 has complete zero-failure phases at 1/4/8/16 clients. Differences in SQL and allocation prevent attribution to READ ONLY alone. Recorded worker cancellations and retry counts remain useful diagnostics; do not rank the aborted c64 runs as clean.

Separately, analysis of captured query `EXPLAIN` plans re-confirms `expt_b3` changes that T6 is fully on index-only scans.

| `->  Index Only Scan using idx_orders_created_at_covering_102104 on public.orders_102104 orders  (cost=0.42..794.50 rows=13104 width=14)` `  Output: created_at, merchant_id, total_amount` `  Index Cond: ((orders.created_at >= '2026-09-11 12:42:13.736861'::timestamp without time zone) AND (orders.created_at < '2026-10-11 12:42:13.736861'::timestamp without time zone))` |
| --- |

*Figure 5.4.2: Snippet of T6 query plan*

## `expt_b5`

The same query plan generated in `expt_b4` discovered that T3 is currently reading all the merchant’s orders from the table via `merchant_id` and then discarding rows not related to `customer_id`.

| `->  Bitmap Heap Scan on public.orders_102124 o  (cost=14.12..1779.77 rows=1 width=32) (actual time=8.631..8.632 rows=0.00 loops=1)` `      Output: o.order_id, o.merchant_id, o.customer_id, o.order_status, o.total_amount, o.created_at` `      Recheck Cond: (o.merchant_id = 1)` `      Filter: (o.customer_id = 1)` `      Rows Removed by Filter: 727` `      Heap Blocks: exact=571` `      Buffers: shared hit=578` `      ->  Bitmap Index Scan on idx_orders_merchant_id_102124  (cost=0.00..14.12 rows=760 width=0) (actual time=0.532..0.533 rows=727.00 loops=1)` `            Index Cond: (o.merchant_id = 1)` `            Index Searches: 1` `            Buffers: shared hit=7` |
| --- |

*Figure 5.5.1: Snippet of T3 query plan in expt_b4*

### Key Changes

1. `CREATE INDEX ... ON orders(merchant_id, customer_id)`

### Benchmark Results and Analysis

|  | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** | **p99 Latency (ms)** |
| --- | --- | --- | --- | --- |
| T3 | 15.83 → 15.80 | 707 → 620 | 990 → 924 | 1,244 → 1,111 |
| Overall | 316.00 → 315.12 | 37 → 41 | 1,242 → 1,263 | 1,656 → 1,650 |

*Table 5.5.1: Comparing expt_b5 against expt_b4 on T3 at 64 clients — flagged raw observations; aborted phases exclude a clean comparison.*

| `->  Index Scan using idx_orders_merchant_customer_102117 on public.orders_102117 o  ...` `Planning Time: 0.633 ms` `Execution Time: 0.306 ms` |
| --- |

*Figure 5.5.2: Snippet of T3 query plan in expt_b5*

The captured T3 shard plan is faster after the merchant/customer index, while T6 remains prominent in recorded time shares. b4 and b5 c64 measurements both abort (b5’s warmup also aborts), so their similar raw TPS is not an eligible matched throughput comparison.

## `expt_b6`

One approach to reduce the amount of data read by analytics queries such as T6 is pre-aggregating and summarising raw tables into rollup tables. In our case, the order counts and revenue per day before the load date can be computed once and reused by every T6.

### Key Changes

1. A new Citus Reference table, `merchant_daily_sales(sales_day, merchant_id, order_count, revenue)`, with primary key `(sales_day, merchant_id)` and the two totals included in the index so it can be read by index-only scans. Reference tables are normally expensive to write, because every write goes to every node, but for this benchmarking experiment, the tradeoff could be worth it since this table is fixed throughout the experiment run.
2. `merchant_daily_sales_cutoff(cutoff_day)`: a one-row plain table on the coordinator that records the first day not in the rollup.
3. At the end of every load, `run.sh` records the cutoff, fills the rollup table with one `INSERT ... SELECT ... GROUP BY` over `orders`, and runs `VACUUM` on it.
4. T6 splits its query window into 3 parts:  the partial first day and the part since the cutoff, both read from orders, plus whole days read from the rollup.

### Benchmark Results and Analysis

|  | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** | **p99 Latency (ms)** |
| --- | --- | --- | --- | --- |
| T6 | 31.05 → 47.90 | 1,266 → 870 | 1,757 → 1,077 | 2,022 → 1,174 |
| T3 | 15.80 → 24.17 | 620 → 161 | 924 → 226 | 1,111 → 261 |
| Overall | 315.12 → 483.53 | 41 → 39 | 1,263 → 869 | 1,650 → 1,031 |

*Table 5.6.1: Comparing expt_b6 against expt_b5 on T6 at 64 clients — flagged raw observations; aborted phases exclude a clean comparison.*

Because this rewrite could silently change T6's answer, we added additional verification. After the load and after every measured run, we run the original T6 query and the new one with the same window and compare all 1,000 per-merchant totals in both directions with `EXCEPT`. We compared the full totals rather than the top 20, because merchants tied for 20th place could legitimately appear in either order. The validation check found 0 differences in all captures.

### Matched baseline comparison and separate correctness run

To compare the final design with the baseline under the same conditions, we also ran b0 and b6 on the same five xcnf nodes. The original b0 run used a different node allocation, so we use the new matched baseline for this comparison.

|  | **TPS** | **p50 Latency (ms)** | **p95 Latency (ms)** | **p99 Latency (ms)** |
| --- | --- | --- | --- | --- |
| b0 | 5.190 | 16.2 | 464.0 | 2679.0 |
| b6 | 108.250 | 4.4 | 56.1 | 61.9 |

*Table 5.6.2: Matched expt_b0 and expt_b6 at 1 client (seed 42). Both runs completed without failed records.*

At 1 client, b6 achieved 20.86 times the baseline throughput, with much lower tail latency. At 4 and 16 clients, b6 completed at 394.380 and 554.982 TPS, while b0 either aborted or recorded final serialization failures. b6 also aborted at 8 clients, so these cases cannot be used for direct speedup comparisons. Five additional T6 checks found no differences across all 1,000 merchants, and a separate correctness job (1031186) subsequently checked negative inventory, order-total equality and duplicate inventory/order-item IDs at three checkpoints with zero violations, and passed a controlled forward/reverse T7 conservation test. Its four-client measurement used 300 seconds and had zero failed records, four retry attempts and phase exits of zero. These separate-run checks do not retroactively validate every earlier benchmark. The matched result shows a large improvement at 1 client, but more runs are needed to confirm the gains at higher concurrency.

# 6. Conclusion

1. The combined A design a112 uses lookup indexes, join-key colocation and READ ONLY declarations; matched runs delivered 16.8–28.2× fresh baseline throughput. a115’s complete audit verifies faster eligible observations, seven phase-complete cases (six with zero failures), all 12 passing validations, and repeated measurement/warmup aborts. For Workload B, the matched experiment showed that b6 achieved 20.86 times the baseline TPS at 1 client. However, aborted runs and serialization failures still limit comparisons at higher client counts. Final A/B choices remain with the team, with all abort/retry and correctness limitations retained.
2. Once joins improved, T6 became the main cost. Pre-aggregation is not automatically faster: a114’s maintained summaries slowed T6 in the A diagnostic, while a115’s timestamp index improved it. Isolated controls, repeated matched runs and explicit abort/retry reporting are essential; passing integrity checks do not make an aborted benchmark clean.
# References

- [Citus README](https://github.com/citusdata/citus): table types, schema-based sharding, Patroni pointer
- [Citus docs: What is Citus](https://docs.citusdata.com/en/stable/get_started/what_is_citus.html): when Citus is inappropriate
- [Citus docs: Concepts](https://docs.citusdata.com/en/stable/get_started/concepts.html): nodes, sharding models and trade-offs, query execution
- [Citus docs: SQL Support and Workarounds](https://docs.citusdata.com/en/stable/develop/reference_workarounds.html): limits table
- [Citus docs: Query Performance Tuning](https://docs.citusdata.com/en/stable/performance/performance_tuning.html): worker tuning method, push-pull rules, connection settings, ingest checklist, COPY rates (read from the docs source repository)
- [Citus docs: Real-Time Dashboards](https://docs.citusdata.com/en/stable/use_cases/realtime_analytics.html): rollup tables
- [Citus docs: create_distributed_function](https://docs.citusdata.com/en/stable/develop/api_udf.html#create-distributed-function)
- [PostgreSQL 18 release notes](https://www.postgresql.org/docs/18/release-18.html): asynchronous I/O, skip scan, `uuidv7()`
- [PostgreSQL 18: io_method](https://www.postgresql.org/docs/18/runtime-config-resource.html)
- [PostgreSQL 18: pgbench](https://www.postgresql.org/docs/18/pgbench.html): init steps, built-in scripts, good practices
- [Citus docs v9.4: Benchmark Setup with Citus and pgbench](https://docs.citusdata.com/en/v9.4/extra/write_throughput_benchmark.html): the older official recipe, single-statement insert and update scripts
