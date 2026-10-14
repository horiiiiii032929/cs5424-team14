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
| expt_a0 | 1 | 26 | 8 | 1.25 | 1.00x | 3290.63 | passed |
| expt_a0 | 4 | 41 | 7 | 1.70 | 1.00x | 11093.77 | passed |
| expt_a101 | 1 | 4525 | 9 | 226.20 | 181.33x | 12.17 | passed |
| expt_a101 | 4 | NA | 0 | NA | NA | NA | FAILED |
| expt_a102 | 1 | 26 | 8 | 1.17 | 0.94x | 3403.20 | passed |
| expt_a102 | 4 | 43 | 7 | 1.98 | 1.17x | 8726.71 | passed |
| expt_a103 | 1 | 20 | 7 | 0.97 | 0.78x | 4437.03 | passed |
| expt_a103 | 4 | 46 | 7 | 1.83 | 1.08x | 9430.98 | passed |
| expt_a104 | 1 | 18 | 7 | 0.90 | 0.72x | 3836.46 | passed |
| expt_a104 | 4 | 45 | 7 | 1.97 | 1.16x | 9060.36 | passed |
| expt_a105 | 1 | 22 | 7 | 1.04 | 0.83x | 2319.75 | passed |
| expt_a105 | 4 | 43 | 7 | 1.55 | 0.91x | 10394.82 | passed |
| expt_a106 | 1 | 22 | 7 | 0.98 | 0.78x | 3427.65 | passed |
| expt_a106 | 4 | 43 | 7 | 1.77 | 1.04x | 9794.45 | passed |
| expt_a107 | 1 | 22 | 7 | 1.08 | 0.87x | 2278.87 | passed |
| expt_a107 | 4 | 30 | 6 | 1.45 | 0.85x | 14973.17 | passed |
| expt_a108 | 1 | 5545 | 9 | 277.25 | 222.25x | 12.08 | passed |
| expt_a108 | 4 | NA | 9 | NA | NA | NA | FAILED |

The next decision requires scale-1 Slurm repeats at 1, 4, 8, 16, 32 and 64 clients
under identical settings. Retain slower variants as experimental evidence. Do not
select a final design solely from this pilot.
