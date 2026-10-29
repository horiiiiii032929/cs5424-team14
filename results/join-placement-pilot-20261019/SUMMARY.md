# Local Docker pilot results

These are short, scale-0.01 implementation measurements on one Mac's Docker VM,
with one coordinator and four workers. They are **not course-cluster benchmarks**.
Check environment.json, each experiment's settings, source hashes and raw logs.
TPS below uses pgbench's elapsed-time denominator; comparison.csv also preserves
the starter-style count / configured-duration metric. Expected business rollbacks
count as completed scripts. One short run cannot establish statistical confidence.
**Small baseline samples and missing transaction types make speedup ratios
exploratory only. Failed runs have no valid throughput and must not be ranked.**

| Experiment | Clients | Completed scripts | Types seen / 9 | TPS | vs baseline | p95 ms | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| expt_a111 | 4 | NA | 0 | NA | NA | NA | FAILED |
| expt_a112 | 4 | NA | 0 | NA | NA | NA | FAILED |

The next decision requires scale-1 Slurm repeats at 1, 4, 8, 16, 32 and 64 clients
under identical settings. Retain slower variants as experimental evidence. Do not
select a final design solely from this pilot.
