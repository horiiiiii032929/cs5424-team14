# Results

## Current status — 22 October 2026

The [B branch import/review](b-branch-review-20261022/README.md) preserves 975
original files and reviews 42 cases. b6/c16 supports 539.437 TPS with both phases
complete; c8 warmup and c32/c64 warmup/measurement aborts are excluded. All seven
saved b6 T6 comparisons match, but runtime hashes and general integrity checks
are not recorded. Hardware differs across the B series.

Both a115 jobs are [fully imported and audited](cluster-full-a115-20261022/README.md)
after VPN reconnection. The 275-file archive verifies 26 runtime hash comparisons,
24 phase commands/exits, raw transaction/retry counts and all 12 validations.
Seven cases complete both phases; six also have zero failed records. Seed-42
c32/c64 and seed-7 c8/c16/c64 measurements abort, as do both c64 warmups.
a112 remains provisional; eligible a115 cases support the index but do not
establish a reliable full matrix. The clean a0/a112 figure is retained.
See [project status](../docs/project-status.md) and [runbook](../docs/workload-a-cluster-runbook.md).

## Verified 19–20 October follow-up

Kelvin's a102/job 965657 source and raw results are now verified, along with his
write-side runs. All six a102 measurements completed, but its 16-client warmup
aborted and is flagged. Clean concurrent observations show 49–57% gains over preserved a0 job 918524,
but only −3% to +6% over the fresh matched-family a0 control 977740.
See the [verified import](cluster-import-20261019/README.md).

Five follow-up variants a109–a113 passed **151 additional correctness checks**.
All seven local four-client stress cases aborted, including the additional
READ ONLY DEFERRABLE test. Failed performance metrics are excluded.
The [course smoke suite](cluster-smoke-20261019/README.md) completed five cases
and aborted three. The [first scale-1 a101 diagnostic](cluster-diagnostic-original-20261019/README.md)
also aborted. Seven deliberate-corruption tests and a 25.753-second full-data
check validated an exact, faster post-run validator. The [revised scale-1 diagnostics](cluster-diagnostic-20261019/README.md)
then completed cleanly: a111/a112/a113 observed 89.9/92.4/90.6 TPS at four clients
over 60 seconds. The [matched full comparison](cluster-full-20261019/README.md)
(a0 977740 and a112 977773, xcnf0–4, 600 s, six client counts) completed with
all exits zero: a112 54.2–90.8 TPS versus a0 3.2–3.6 TPS (17–28×), no failed
transactions, and passing validation at every count. T6 now dominates a112's time.
See [live cluster work](cluster/README.md).
Seed-7 repeat 978177 agreed within 2.5% (64-client warmup abort flagged).
a112 is the provisional A selection, pending Kelvin's review.
See the [A report draft](../docs/workload-a-report-draft.md) and
[cluster runbook](../docs/workload-a-cluster-runbook.md).

a114 (a112 + exact daily sales summaries, eight stripes per merchant/day, and a
T6 that reads raw orders only for the two partial days) passed
[42 correctness checks](correctness-summary-20261019/README.md). In the
[local pilot](summary-pilot-20261019/README.md) it completed at one client
(285 vs a112's 306 TPS on the 50k-order fixture) and aborted at four clients,
like a112. A [1M-order T6 check](t6-plan-check-20261019/README.md) measured
25.5 ms versus 78.0 ms for a112's query, but 17.0 ms for the original query
with only the `created_at` index. Completed cluster diagnostics 979865/979866
confirmed that a114 is slower: 85.333 TPS versus a115's 288.633 TPS, with T6
764.5 versus 115.9 ms. Both validated; a115 had two retried transactions and no
failed transactions. a114 is not promoted. For a115 full-run aborts and the remaining archive audit, see the 22 October status above.
See [T6 diagnostic evidence](cluster-diagnostic-t6-20261020/README.md).

## Original results — 14 October 2026

All five of Hikaru's Workload A proposals are implemented. They produce seven
individual experiments and one combined experiment. The local distributed
correctness suite passed **138 checks**. The benchmark matrix attempted **18
cases: 16 completed with passing integrity checks and two aborted**.

**These are short local pilot results, not the final course-cluster results.**
They identify promising ideas and a concurrency problem to investigate; they do
not establish a final winning design.

## What the pilot found

TPS means completed pgbench scripts per second, including expected business
rollbacks. Each case used a fresh scale-0.01 dataset, a five-second warmup and a
20-second measurement. All nine transaction types kept their prescribed weights.

| Experiment | What changed | 1 client TPS | 4 clients TPS |
|---|---|---:|---:|
| a0 | Supplied baseline | 1.25 | 1.70 |
| a101 | Keep merchant data together | 226.20 | **Aborted in warmup** |
| a102 | Add lookup indexes | 1.17 | 1.98 |
| a103 | Place an order in one function call | 0.97 | 1.83 |
| a104 | Maintain exact daily sales totals | 0.90 | 1.97 |
| a105 | Increase work_mem from 32MB to 64MB | 1.04 | 1.55 |
| a106 | Reduce executor pool from 4 to 2 | 0.98 | 1.77 |
| a107 | Increase executor pool from 4 to 8 | 1.08 | 1.45 |
| a108 | Combine placement, indexes, function and sales totals | 277.25 | **Aborted during measurement** |

Merchant colocation showed the strongest one-client signal. However, the
baseline completed only 26 scripts at one client and 41 at four clients, with
some transaction types absent from those samples. The apparent speedup needs
longer, repeated runs. The other individual changes showed no clear overall
improvement in this short pilot; their small samples cannot support a reliable
ranking.

The two failed four-client cases reported serialization conflicts followed by
failed distributed commits. For a108, pgbench exited with code 2 and explicitly
reported incomplete results. Its partial TPS is retained in the raw output but
excluded from the comparison. All five core data-integrity checks passed after
each failure; a108 also passed all five summary/report checks. This does not
resolve the concurrent benchmark failure or prove correctness for all schedules.
Keep serializable isolation while investigating.

- [Full comparison, sample counts and tail latencies](local-native-20261014/SUMMARY.md)
- [CSV data](local-native-20261014/comparison.csv)
- [Environment, versions and settings](local-native-20261014/environment.json)
- [a101 failure and post-failure checks](local-native-20261014/expt_a101/c4/failure.json)
- [a108 raw aborted measurement](local-native-20261014/expt_a108/c4/pgbench.txt)
- [a108 post-failure checks](local-native-20261014/expt_a108/c4/failure.json)

## Correctness and reproducibility

[All 138 native correctness checks passed](correctness-native-20261014/README.md).
They cover orders, business rejection and rollback, duplicate products, competing
orders, inventory transfers, generated IDs, order totals, and exact sales reports.
This smaller correctness fixture is separate from the performance dataset.

The pilot used native ARM PostgreSQL 18.6 / Citus 14.1.0, one coordinator and four
workers on a single Docker VM with eight CPUs and about 8GB RAM. Each benchmark
folder includes its source hashes, effective settings, fixture size, raw logs and
validation outcome. See [provenance](local-native-20261014/PROVENANCE.md) for the
suite restart and exact harness snapshot.

An earlier AMD64 run under emulation was rejected after a worker crash.
[Its diagnostics are retained](local-pilot-20261014/README.md); do not use its
timings for design comparisons.

## What remains for the course submission

1. Confirm A with Kelvin using the completed a115 audit and its phase/failure
   classifications; neither full a115 seed is a clean six-count matrix.
2. Preserve a112's flagged seed-7/c64 warmup and all earlier local/smoke aborts.
   The commit-time serialization issue is not established as generally resolved.
3. Confirm B selection using the archived review; retain all abort/hardware caveats and fill core validation/runtime provenance gaps.
4. Confirm both final designs, contribution statements and AI records, then
   assemble the report and submission archives. See the [current action list](../docs/project-status.md).

At the 14 October checkpoint, SoC SSH timed out before authentication and no
new Slurm jobs had been submitted. Access was restored on 19 October; see the
current follow-up above. Existing team files remain preserved. Isolated upload
and submission commands are in the [main README](../README.md).

## Dessi's existing course-cluster baselines

- [Workload A, job 918524](../citus_project_team_14/expt_a0/slurm-results/job-918524/benchmark-results/)
- [Workload B, job 918781](../citus_project_team_14/expt_b0/slurm-results/job-918781/benchmark-results/)

These snapshots are preserved unchanged. Workload A at one client achieved
3.220 TPS; average T3 latency was 2678.797 ms. Baseline A contains serialization
failures at 16/32/64 clients. Baseline B includes pgbench exit 2 at 8/16 clients;
investigate those failures before treating them as clean comparisons. Their
hardware and dataset differ from the local pilot, so do not compare their TPS
directly with the table above.
