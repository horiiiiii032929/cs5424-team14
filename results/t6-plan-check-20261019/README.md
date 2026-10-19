# T6 plan and latency check — 19 October 2026

**Local Docker only (native ARM PostgreSQL 18.6 / Citus 14.1.0, one coordinator,
four workers). Not a course-cluster result.** Scale 0.2 fixture: 200 merchants,
1,000,000 orders, 3,000,000 items, loaded with a114's schema (a102 indexes,
join colocation, striped `sales_daily`, `orders(created_at)` index). One client,
REPORT_DAYS=30, SERIALIZABLE, no concurrent load.

| T6 variant | Median latency, 3 × 50 runs (ms) |
|---|---:|
| a112 original query, no `created_at` index (as in a112) | 78.0 |
| a104 summary T6 | 39.2 |
| a114 two-range summary T6 | 25.5 |
| original query with only the `orders(created_at)` index | 17.0 |

Why a114 changed a104's T6: a104's raw branch filters
`[lo, hi) AND NOT [first_day, last_day)`, so its index condition is the whole
30-day window and the whole days are removed afterwards (`a104_summary-explain.txt`:
"Rows Removed by Filter"). a114 scans only `[lo, first_day)` and `[last_day, hi)`
via a BitmapOr, with bounds still computed once. Results are identical by
construction and are tested (`exact_report_{0,1,30,365}_days`, top-20 check).

**Confound:** in this local setting the summary T6 is slower than the original
query given just the `created_at` index that a104/a114 also add. The summary costs
four Citus subplan round trips; the indexed scan reads ~8% of orders. At scale 1
(5M orders, 1,000 merchants) the balance may differ, so a cluster comparison needs
an "a112 + created_at index only" control before crediting the summary itself.

Files: `queries/*.sql` (exact scripts timed), `*-pgbench.txt`, `*-explain.txt`
(EXPLAIN ANALYZE), `latency-ms.json` (first single pass, cache-order effects),
`latency-rounds.json` (interleaved rounds used above), `t6_scale_check.py` and
`t6_rounds.py` (harness; scale overrides patch the local loader's counts).
`setup/code-sha256.json` predates adopting the two-range T6 in a114; the timed
query text is in `queries/`.
