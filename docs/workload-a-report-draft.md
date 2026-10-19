# Draft report sections 2–3: Workload A

Prepared 19 October 2026. This is a working draft; the final design and cluster
comparisons remain open. Kelvin's a102/a10/a11/a12/a14 update is recorded in
`results/team-update-20261019/kelvin-update.json` as teammate-reported evidence.
Its raw cluster files have not yet been retrieved and checked here.

## 2. Task 1: Baseline design for workload A

### 2.1 Environment and workload

The preserved baseline, `expt_a0`, ran as Slurm job 918524 on five xcnf nodes:
one coordinator and four workers. It used PostgreSQL 18.6 and Citus 14.1.0,
scale 1, SERIALIZABLE isolation, 60-second warmup, 600-second measurements,
and full transaction-log sampling. The coordinator was xcnf8. Each node received
four CPUs. The database settings included shared_buffers 1GB, work_mem 32MB and
an adaptive executor pool limit of 4.

The workload weights for T1–T9 were 36/20/10/10/10/5/5/2/2 percent.
Orders and items were distributed by their individual generated identifiers,
while inventory was distributed by inventory_id. Although the distribution-key
types permitted a shared colocation group, the joins did not consistently match
those distribution keys. Merchant/customer filters therefore did not make the
order-history join local to one worker.

### 2.2 Baseline results

Values below come from the preserved job's `summary.csv`, not the local pilot.
TPS is completed pgbench scripts divided by configured measurement duration.
Completed scripts can include expected business rejections.

| Clients | TPS | p50 ms | p95 ms | p99 ms | Retried transactions | Serialization failures | pgbench exit |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3.220 | 11.009 | 2654.656 | 2698.524 | 0 | 0 | 0 |
| 4 | 2.283 | 22.897 | 15398.450 | 18331.968 | 1 | 0 | 0 |
| 8 | 2.285 | 34.815 | 29532.561 | 32842.913 | 13 | 0 | 0 |
| 16 | 2.368 | 41.305 | 52999.831 | 58194.283 | 49 | 25 | 0 |
| 32 | 2.405 | 41.395 | 92368.465 | 100724.606 | 67 | 51 | 0 |
| 64 | 2.283 | 54.925 | 180370.276 | 187011.576 | 62 | 50 | 0 |

At one client, T3 averaged 2678.797 ms, T4 458.862 ms, and T7 51.114 ms.
Throughput did not scale with additional clients, while tail latency increased
substantially. The 16/32/64-client cases completed with nonzero serialization
failure counts. These failures must remain visible in the comparison even
though pgbench returned zero.

The results suggest prioritizing T3/T4 data access and placement before further
optimizing short update transactions. Query plans from the new cluster runs
are still needed to verify the execution mechanism directly for A.
Weighting each transaction's observed mean latency by its completed count,
T3/T4 account for approximately 93.6% of recorded transaction time at one client
and 97.2% at 64 clients. This is a time-share calculation, not their workload weights.

## 3. Task 2: Optimized design for workload A

### 3.1 Individual designs

Hikaru implemented five design angles as seven individual variants and a
combined design. All preserve the workload mix and required isolation.

| Experiment | Change | Purpose or tradeoff |
|---|---|---|
| a101 | Merchant-based placement and matching join predicates | Reduce distributed work; examine hot-merchant contention and cross-merchant work. |
| a102 | Order lookup, order-item and inventory lookup indexes | Reduce lookup cost; measure write overhead and remaining distributed joins. |
| a103 | One-call T1 function | Reduce round trips while preserving atomic stock/order/item changes and business rollback. |
| a104 | Exact daily sales summaries | Reduce T6 scanning while maintaining totals synchronously inside T1. |
| a105 | work_mem 64MB | Isolate a memory-setting change from placement and SQL changes. |
| a106/a107 | Executor pool 2/8 | Compare worker concurrency with the baseline limit of 4. |
| a108 | Placement + indexes + T1 function + sales summaries | Measure interactions between changes. |

The native distributed correctness suite passed 138 checks on the original
variants, including rejected orders, duplicate products, rollback after partial
work, competing orders, transfers, generated IDs, order totals and exact reports.
The original short local pilot completed 16 of 18 cases. a101 aborted during
four-client warmup and a108 during four-client measurement. Their partial
performance measurements are excluded from comparisons.

### 3.2 Course-cluster evidence reported by Kelvin

Kelvin ran a102 unchanged from commit 82058e6 as job 965657, with results under
`/home/stuproj/cs14/citus_project/expt_a102`. He reports 3.25 TPS at one client
and 3.40 TPS at 64 clients, versus 3.220 and 2.283 in the preserved baseline.
These endpoints imply approximately 0.9% and 48.9% higher throughput respectively;
they are single-run observations, not confidence estimates. Kelvin reports
40–65% improvement from four clients upward, zero serialization failures, and
passing verify.sql at every client count. The full six-client matrix, node
topology, raw logs and source hashes still require independent review here.

He reports T7's one-client average latency falling from about 51 to 14 ms,
but T3/T4 remaining about 2.67 s / 454 ms and together roughly 94% of time.
This supports testing colocation as the next step rather than expecting lookup
indexes alone to remove distributed joins.

Kelvin's separate experiments on top of a102 are a10 (autocommit T2/T5/T8/T9),
a11 (fillfactor 80), a12 (synchronous_commit off), and a14 (VACUUM only).
He reports no material overall TPS gains. a10 had a T1 client abort at 32
clients; its affected measurement must not be treated as a valid full-client
performance result. a11's zero-retry observation needs repetition. These are
Kelvin's experiments and should be attributed accordingly in contributions.

### 3.3 Follow-up: read-only access declarations

The team B report describes a reduction in client aborts after declaring T3/T4/T6
READ ONLY. To test that hypothesis independently for A, a109 derives from a101
and a110 from a108, changing only those three BEGIN statements to BEGIN READ
ONLY. Their query bodies, write transactions, isolation, retry limit, workload
weights and durability settings are unchanged. No DEFERRABLE mode is added.
The new Slurm scripts select xcnf hardware; all submissions through the helper
now do so as well. Hardware selection is recorded separately from the SQL change.

READ ONLY is an access mode, independent of the isolation level. It does not
guarantee that SERIALIZABLE transactions will avoid all serialization failures.
The original failed variants are preserved for matched comparisons.

On 19 October, the follow-up local test reproduced four-client aborts in a101,
a108, a109 and a110. The read-only variants passed 64 correctness checks in total,
but did not resolve the benchmark failures. No partial TPS from these aborted
runs is used as a performance result.

### 3.4 Alternative: colocate on the join keys

a111 adapts Dessi's B b1/b2 placement changes to A on top of a102. Inventory is
distributed by product_id and colocated with products; order_items is distributed
by order_id and colocated with orders. T7 retains the selected inventory ID and
adds its corresponding product ID to each update's routing predicate. This does
not assume that inventory_id equals product_id. a112 changes only T3/T4/T6's access
declarations to READ ONLY relative to a111. Dessi's original design contribution
and Hikaru's A adaptation are both recorded in the experiment manifests.

Both variants passed 29 correctness checks each, including T7 with inventory IDs
deliberately different from product IDs, actual distribution/colocation metadata,
and the real read transaction scripts. T3/T4/T6 EXPLAIN ANALYZE plans for a112
were captured on the small correctness fixture. Performance validation is recorded
separately from that fixture; these checks do not establish course-cluster speedup.
Both a111 and a112 aborted during the local four-client warmup. Together with
the four merchant-colocation cases above, all six follow-up stress cases failed.
All 40 post-failure integrity checks passed. No failed TPS is used in a ranking;
the next decision requires diagnostic cluster runs and review of Kelvin's raw data.

### 3.5 Final comparison still required

Run matched baseline/index/colocation comparisons on xcnf nodes at scale 1 with
1/4/8/16/32/64 clients, 60-second warmup and 600-second measurements. Retain
source hashes, actual topology, retries, failed transaction counts, nonzero exits,
validation and per-transaction latency. Repeat promising variants with recorded
seeds. Confirm new experiment IDs with Kelvin before uploading into the shared
account; use an isolated directory.

No final A design or definitive speedup is claimed in this draft. Local timing
and teammate-reported cluster numbers remain separate from independently
verified course-cluster measurements.

## Sources to retain in the final report

- Preserved expt_a0 job 918524: config.txt, summary.csv, transaction_metrics.csv,
  topology and server versions in the repository.
- Kelvin's supplied update, indexed in results/team-update-20261019/kelvin-update.json.
- Native correctness and local pilot records in results/.
- [PostgreSQL 18 SET TRANSACTION](https://www.postgresql.org/docs/18/sql-set-transaction.html).
- [Citus colocation](https://github.com/citusdata/citus/blob/main/README.md#creating-distributed-tables-with-co-location).

## Hikaru contribution draft

Designed and implemented A variants a101–a112 (including adaptation of Dessi's
B placement design for a111/a112); built experiment generation,
distributed correctness checks, local benchmark infrastructure and submission
helpers; preserved evidence and failures; established the public team repository;
drafted A analysis and coordinated packaging. Kelvin ran cluster a102 and owns
a10/a11/a12/a14. Dessi supplied original A/B baselines and the B experiment/report
work. Confirm full names and remaining contributions with the team before submission.
