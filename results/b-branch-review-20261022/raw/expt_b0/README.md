# expt_b0 — Baseline, workload B

- **Status:** run.
- **Change from previous version:** none. This is the provided baseline design.
- **Question it answers:** where does the time go?
- **Job id:** 918781, on 2026-10-07, nodes `xcnf[8-12]`.
- **Data load time:** about 3 min 45 s per reload. The whole job took 1 h 37 min.

## Critical stats

| Stat | Value |
| --- | --- |
| Peak throughput | 3.77 TPS, at 1 client |
| Throughput at 64 clients | 3.19 TPS |
| p99 latency, 1 client to 64 clients | 4.0 s to 160 s |
| T3 average latency, 1 client | 4,037 ms |
| T3 share of all time | 68% at 1 client, 63% at 16 |
| T3 + T6 + T4 + T7 share of all time | over 99% |
| T7 average latency, 1 client | 66 ms, of which 63 ms is its four lookups |
| Serialization failures at 64 clients | 493, or 20% of transactions |
| Single-shard update (T2), 1 client | 1.5 ms, of which 0.38 ms is commit |
| T7 two-phase commit, 1 client | 1.1 ms |

## Overall

From `summary.csv`. TPS there is transactions divided by 600 s; the runs actually lasted 603 to 649 s because in-flight transactions finish after the timer.

| Clients | TPS | Avg ms | p50 ms | p95 ms | p99 ms | Retried | Serialization failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3.77 | 266 | 14 | 666 | 4,013 | 0 | 0 |
| 4 | 3.46 | 1,163 | 44 | 12,917 | 17,040 | 77 | 10 |
| 8 | 3.64 | 2,080 | 59 | 6,736 | 31,323 | 245 | 101 |
| 16 | 3.54 | 4,007 | 36 | 25,595 | 53,878 | 468 | 267 |
| 32 | 3.17 | 8,560 | 32 | 75,582 | 90,242 | 490 | 340 |
| 64 | 3.19 | 15,349 | 35 | 133,192 | 160,032 | 633 | 493 |

No deadlock failures at any client count.

## Per transaction

From `transaction_metrics.csv`. Share of time is count times average latency, as a fraction of the total.

| Txn | Avg ms, 1 client | Share of time, 1 client | Avg ms, 16 clients | Share of time, 16 clients |
| --- | --- | --- | --- | --- |
| T3 | 4,037 | 67.6% | 48,790 | 62.6% |
| T6 | 399 | 15.1% | 3,490 | 9.2% |
| T4 | 633 | 9.5% | 11,651 | 15.5% |
| T7 | 66 | 7.2% | 2,408 | 12.5% |
| T1 | 11 | 0.4% | 52 | 0.2% |
| T2, T5, T8, T9 | 1.4 to 1.6 each | 0.1% each | 7 to 10 each | under 0.1% each |

## Findings

- **Throughput is flat at about 3.5 TPS regardless of clients.** Adding clients only adds latency.
- **T3 takes about two thirds of all time** at 5% of the mix. T3, T6, T4 and T7 together take over 99%.
- **T7's four lookups cost 14 to 19 ms each** at 1 client, 63 of T7's 66 ms. Its commit is 1.1 ms.
- **Serialization failures grow with clients**, up to 20% of transactions at 64.
- **The single-shard updates are fast**: about 1.5 ms, of which the commit is 0.4 ms.

## Problems during the run

- **pgbench exit code 2 at 8 and 16 clients.** One client aborted in each run with `could not commit transaction for shard ... on at least one active node`. The cause was a serialization failure raised at commit time on a worker. Citus reports it as a generic error, so pgbench does not retry it and stops that client for the rest of the run.
