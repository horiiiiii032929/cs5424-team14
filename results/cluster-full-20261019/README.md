# Matched full Workload A comparison — 19 October 2026

Both jobs ran from the isolated deployment
`/home/stuproj/cs14/citus_hikaru_20261019-172259_cf48c8d` (cf48c8d experiment
source) on the same explicitly requested nodes: xcnf0 coordinator, xcnf1–4
workers. Scale 1, SERIALIZABLE, original A weights, 60-second warmup, 600-second
measurement, data reset between client counts, pgbench seed 42, full log sampling.

| Clients | a0 TPS | a112 TPS | Ratio | a0 p95 ms | a112 p95 ms | a0 serialization failures | a112 serialization failures | a112 retried |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3.225 | 54.238 | 16.8× | 2645.3 | 19.7 | 0 | 0 | 0 |
| 4 | 3.565 | 85.042 | 23.9× | 9822.8 | 313.6 | 0 | 0 | 0 |
| 8 | 3.568 | 87.378 | 24.5× | 19276.3 | 978.3 | 2 | 0 | 2 |
| 16 | 3.282 | 88.073 | 26.8× | 36030.5 | 2407.6 | 20 | 0 | 2 |
| 32 | 3.613 | 90.660 | 25.1× | 64187.6 | 623.0 | 64 | 0 | 5 |
| 64 | 3.222 | 90.788 | 28.2× | 128104.3 | 6597.9 | 59 | 0 | 16 |

TPS = completed scripts / 600 s. Jobs: a0 977740, a112 977773.
All 12 warmup and measured pgbench exits are zero. a112 wrote six passing
`verify.sql` records (one per client count). The unmodified a0 starter script
has no post-run validation step; its case-review rows record `not_in_script`.
Slurm state alone was not trusted — see `case-review.csv` (built by
`scripts/import_cluster_jobs.py`) and `import-manifest.json` for hashes.

Per-transaction, one client: T3 2656.9 → 6.8 ms, T4 454.5 → 1.5 ms,
T7 51.7 → 5.3 ms; T6 is unchanged (263.0 → 256.9 ms). Weighted by completed
count × mean latency, T3+T4 are 93.5–97.7% of a0's recorded time, while T6 is
67–83% of a112's. T6 (Global Sales) is now the dominant remaining cost; at 64
clients T3 also rises to 1.69 s mean as contention grows.

## Consequence for earlier comparisons

The fresh a0 on xcnf0–4 completes 3.22–3.61 TPS, higher than preserved job
918524 (2.28–2.41 TPS) at 4+ clients. Kelvin's a102 job 965657 (xcnf1–5)
recorded 3.25–3.78 TPS. Against this fresh baseline, a102's clean throughput
differences are −3.1% to +5.5% rather than the earlier 49–57%; its clear
benefits remain zero serialization failures and faster T7. The nodes are not
identical, so neither comparison is a matched a102 result.

## Pending

Repeat a112 with pgbench seed 7 (job 978177, same nodes, queued after 977773)
was submitted to check run-to-run stability. Its results are not in this table.
