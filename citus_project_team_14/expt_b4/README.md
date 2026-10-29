# expt_b4 — Read-only declarations and a literal T6 window

Built on `expt_b3`. Not yet run.

| # | File | Where | Change |
| --- | --- | --- | --- |
| 1 | `T3_order_history.sql`, `T4_product_lookup.sql`, `T6_global_sales.sql` | the `BEGIN` line of each | `BEGIN;` becomes `BEGIN READ ONLY;` |
| 2 | `T6_global_sales.sql` | [lines 3 to 14](transactions/T6_global_sales.sql#L3-L14) | The window is read once with `LOCALTIMESTAMP`, then passed to the query as two literal timestamps. |
| 3 | `run.sh` | [lines 516 to 532](run.sh#L516-L532) | Saves `EXPLAIN VERBOSE` and `EXPLAIN ANALYZE` output for T6, T3 and T5 to `query-plans.log` in the job folder. Runs once after the first load. |

The schema and the other six scripts are the same as in `expt_b3`.

Changes 1 and 2 both alter behaviour. The abort counts isolate change 1, and T6's latency with `query-plans.log` isolates change 2.

## 1. Read-only declarations

In `expt_b3`, clients aborted in large numbers: 22 of 64 by the end of the 64-client run. Each abort was a transaction cancelled at commit time by PostgreSQL's SERIALIZABLE conflict tracking, on the commit path that pgbench cannot retry.

PostgreSQL cancels a transaction when it finds a chain of two read-then-changed dependencies among concurrent transactions. It skips a chain whose first member is a read-only transaction. T6 reads a wide range of `orders` that T1 inserts into, which makes it the likeliest first member.

- **Measure:** client aborts and T1's commit retries against `expt_b3` (22 aborts and 327 retries at 64 clients).
- **Not verified:** that Citus passes the read-only flag to the workers.

## 2. Literal window for T6

Before, each worker evaluated `CURRENT_TIMESTAMP` itself. Now the coordinator reads the time once and every shard gets the same two literal timestamps.

- **The comparison is now `timestamp` against `timestamp`.** Before it was `timestamp` against `timestamptz`, which converts on every row. That conversion is one of three suspects for T6's remaining cost.
- **It costs one more round trip**, to the coordinator only.
- **Same rows as before** as long as the server's time zone has no daylight saving. The logs show `+08`.
- **Measure:** T6's latency at 1 client against `expt_b3` (65 ms).

## 3. Plan capture

`query-plans.log` holds, for the design in this folder:

- T6: `EXPLAIN VERBOSE`, then `EXPLAIN (ANALYZE, VERBOSE, BUFFERS)` twice. Read the second one.
- T3: `EXPLAIN VERBOSE` and one `EXPLAIN (ANALYZE, VERBOSE, BUFFERS)`.
- T5: `EXPLAIN VERBOSE` only, so the update is not executed.

What to look for in T6: the scan type on the shard, `Heap Fetches`, and the task's execution time against the total.

## Considered and left out: partitioning `orders` by month

- **Little to gain for T6.** The covering index already limits each shard to the entries inside the window. Skipping other months would not reduce what is read.
- **A cost for a quarter of the mix.** T5, T1's final update and T3 do not carry `created_at`, so each would search every partition of a shard.

It can be its own experiment later if the plan shows T6 is not using the index as intended.
