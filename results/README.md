# Results — 14 October 2026

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

1. Reproduce and investigate the four-client colocation/combined failures on the
   course cluster, without weakening isolation or changing the workload.
2. Once the smoke runs are reviewed, run scale-1 measurements at 1, 4, 8, 16, 32
   and 64 clients, with the original 60-second warmup and 600-second measurement.
   Repeat promising designs to assess variability; report aborts and retries.
3. Choose the final design from that evidence. Retain unsuccessful experiments
   as useful findings and match report experiment IDs to the submitted folders.

SoC SSH timed out before authentication on 14 October. No new Slurm jobs have
been submitted and no existing team-cluster files were changed. The isolated
upload and submission commands are in the [main README](../README.md).

## Dessi's existing course-cluster baselines

- [Workload A, job 918524](../citus_project_team_14/expt_a0/slurm-results/job-918524/benchmark-results/)
- [Workload B, job 918781](../citus_project_team_14/expt_b0/slurm-results/job-918781/benchmark-results/)

These snapshots are preserved unchanged. Workload A at one client achieved
3.220 TPS; average T3 latency was 2678.797 ms. Baseline A contains serialization
failures at 16/32/64 clients. Baseline B includes pgbench exit 2 at 8/16 clients;
investigate those failures before treating them as clean comparisons. Their
hardware and dataset differ from the local pilot, so do not compare their TPS
directly with the table above.
