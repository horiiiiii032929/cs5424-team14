# T6 follow-up diagnostics — 20 October 2026

After the matched full run, T6 (Global Sales) was 67–83% of a112's recorded
time. Two variants of a112 were built on branch `expt-a114-sales-summary`
(commit 57576ae) and deployed to
`/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae`:

- **a114**: a112 + a104's exact daily sales summaries, striped eight ways per
  merchant/day and maintained inside T1; T6 reads the summary plus the two
  partial-day order ranges (also adds the `orders(created_at)` index).
- **a115**: a112 + only the `orders(created_at)` index, with a112's original
  T6 query. This is a114's control: a local scale-0.2 timing check found the
  original query with this index faster than either summary T6.

Both ran the standard diagnostic on xcnf0–4: scale 1, four clients, 60 s
warmup + 60 s measurement, seed 42. Compared with a112 diagnostic 977618:

| Experiment | Job | TPS (count / 60 s) | T1 ms | T3 ms | T6 ms | T6 p95 ms | Failed / retried | Validation |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| a112 | 977618 | 92.383 | 22.9 | 29.2 | 650.6 | — | 0 / 0 | passed |
| a114 | 979865 | 85.333 | 20.6 | 23.4 | 764.5 | 1041.9 | 0 / 0 | core + summary passed |
| a115 | 979866 | 288.633 | 15.7 | 10.7 | 115.9 | 161.9 | 0 / 2 | passed |

All warmup and measured exits are zero. a115 retried two transactions (two total
retry attempts); neither failed. The counts match both summary.csv and raw
pgbench output. On the cluster the summary T6 is
*slower* than a112's scan (764 vs 651 ms): its extra distributed subplan round
trips outweigh the rows saved. The plain `created_at` index cuts T6 by 82% and,
because T6 no longer holds workers for hundreds of milliseconds, every other
transaction speeds up too: throughput is 3.1× a112's diagnostic.

a114 is therefore not promoted. a115 advances to a full matched run (979909,
seed 42) and a repeat (979910, seed 7) on xcnf0–4. They were submitted and last
recorded as queued; their current state/results could not be verified during the
20 October SSH timeout. Single 60-second observations do not establish a final
ranking; review both full runs before promotion.
