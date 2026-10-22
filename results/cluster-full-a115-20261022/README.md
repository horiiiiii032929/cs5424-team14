# Full a115 import and audit — 22 October 2026

Both finished jobs are fully imported from
`/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae` after VPN access returned.
This supersedes the [earlier partial transcription](../a115-readback-20261022/README.md),
which remains as a historical checkpoint. The 275 imported files preserve both
jobs' complete pgbench logs, transaction metrics, worker logs, Slurm output,
settings, topology, validators, runtime hashes and the actual SQL/source files.

[Import manifest](import-manifest.json) records file SHA-256 checksums, the original
archive digest and the supplemental SQL/source archive digest.
[Case review](case-review.csv), [detailed audit](audit.json) and
[Slurm/queue snapshot](slurm-accounting-and-queue.txt) retain the evidence.
Reproduce the audit without executing benchmarks:

```sh
python3 scripts/review_a115_results.py results/cluster-full-a115-20261022
```

## Full matrix

TPS is completed scripts / configured 600 seconds, including expected business
rollbacks. Raw TPS is retained even for excluded cases. Phase eligibility means
both exits are zero and post-run validation passed; it does not imply zero
failed transactions. There are **7 phase-eligible cases, 6 with zero failures**.

| Seed / job | Clients | Raw TPS | Warmup / measured exit | Failed records | Retried transactions / retries | Classification |
|---|---:|---:|---|---:|---|---|
| 42 / 979909 | 1 | 115.485 | 0 / 0 | 0 | 0 / 0 | Eligible, zero failures |
| 42 / 979909 | 4 | 296.697 | 0 / 0 | 1 | 8 / 9 | Eligible phases; retain one serialization failure |
| 42 / 979909 | 8 | 335.585 | 0 / 0 | 0 | 27 / 28 | Eligible, zero failures |
| 42 / 979909 | 16 | 323.213 | 0 / 0 | 0 | 44 / 45 | Eligible, zero failures |
| 42 / 979909 | 32 | 325.640 | 0 / 2 | 0 | 221 / 226 | Excluded: measurement abort |
| 42 / 979909 | 64 | 366.145 | 2 / 2 | 0 | 395 / 406 | Excluded: both phases abort |
| 7 / 979910 | 1 | 109.893 | 0 / 0 | 0 | 0 / 0 | Eligible, zero failures |
| 7 / 979910 | 4 | 276.233 | 0 / 0 | 0 | 11 / 12 | Eligible, zero failures |
| 7 / 979910 | 8 | 323.378 | 0 / 2 | 1 | 67 / 72 | Excluded: measurement abort |
| 7 / 979910 | 16 | 325.860 | 0 / 2 | 2 | 105 / 108 | Excluded: measurement abort |
| 7 / 979910 | 32 | 330.600 | 0 / 0 | 0 | 206 / 211 | Eligible, zero failures |
| 7 / 979910 | 64 | 355.620 | 2 / 2 | 7 | 610 / 659 | Excluded: both phases abort |

Both jobs have six passing post-measurement core validations, including excluded
cases. All 12 validation blocks commit, with no ERROR or ROLLBACK. Passing
integrity checks do not erase client aborts or prove correctness for all schedules.
Slurm reports COMPLETED/0:0 for both jobs because run.sh retains nonzero pgbench
exits and continues; neither job is a clean six-count benchmark matrix.

## Source and protocol verification

All **13 runtime SHA-256 entries per job** match both the imported source and
repository a115 source: run.sh, nine transaction scripts and three SQL files.
The a115 transaction bodies match a112. The sole runtime design addition is
`orders(created_at)` via sql/report_time_index.sql, with ANALYZE; run.sh invokes
that file. The saved runner invokes that SQL before loading data; runtime hashes identify
the exact source.

Both saved configurations, all 24 pgbench command lines, reset logs, topology and
version records confirm xcnf0 coordinator/xcnf1–4 workers, scale 1, PostgreSQL
18.6/Citus 14.1.0, SERIALIZABLE, original A weights, data seed 42, pgbench seeds
42/7, 60 s warmups, 600 s measurements, full sampling, retry limit 3, and fresh
data before every client count. Configured pgbench client counts match their
labels; aborting clients stop participating, so affected measurements are excluded.

The audit independently tallies all 12 raw transaction logs: successful and
failed records, per-script completed counts, serialization failures, retried
transactions and retry attempts agree with summary.csv/transaction_metrics.csv.
The earlier transcribed summary rows exactly match the imported originals.

## Failure review

Seed 42: c32/c64 measurements each lose one T1 client; c64 warmup loses one T1
client. Seed 7: c8 loses one T1 client, c16 loses five T1 clients, and c64 loses
eight clients (six T1, one T2 and one T9); c64 warmup loses two T1 clients.
All these abort messages report `could not commit transaction for shard`.
Worker logs also retain SERIALIZABLE dependency-pivot cancellations during
commit attempts; examples are recorded in audit.json. These observations are
consistent with the previously documented wrapped commit-time conflict, rather
than evidence that READ ONLY or the timestamp index generally fixes concurrency.
Not every individual abort has a separately traced causal chain.

Zero failed transaction rows are insufficient: seed-42 c32/c64 exit 2 despite
zero such rows. Client-abort messages and phase exit codes must remain visible.
No aborted raw TPS is ranked as eligible, including the apparent 366.145 TPS peak.

## Comparison and decision

At one client, both a115 seeds complete without failures: 115.485/109.893 TPS,
versus a112's same-seed 54.238/52.970 TPS (2.13×/2.07×). Seed-42 c8/c16 and
seed-7 c32 are also phase-eligible with zero failures and show approximately
3.7–3.8× their corresponding a112 observations. Seed-42 c4 completes both phases
at 296.697 TPS but has one failed serialization transaction; seed-7 c4 completes
at 276.233 TPS with no failures. Comparisons retain these distinctions.

The index has supported performance value in eligible cases, but the full runs
do not establish a reliable high-concurrency matrix or clean repeat at every
count. a112 remains provisional, including its own seed-7/c64 warmup caveat.
Kelvin and the A pair must confirm the final performance/reliability tradeoff.
The clean matched a0/a112 figure is retained; no incomplete a115 case is silently
added to its ranking. This review submitted no new jobs and changed no benchmark SQL.
