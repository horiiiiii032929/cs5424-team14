# expt_b5 — Index for T3

Built on `expt_b4`. Not yet run.

| # | File | Where | Change |
| --- | --- | --- | --- |
| 1 | `run.sh` | [line 436](run.sh#L436) | `CREATE INDEX idx_orders_merchant_customer ON orders(merchant_id, customer_id)` |
| 2 | `run.sh` | [lines 1329 to 1330](run.sh#L1329-L1330) | Saves the same query plans again after each measured run, to `query-plans-after-c<clients>.log`. Diagnostic only. |

No transaction script changes.

## 1. Index for T3

T3 asks for one customer's orders at one merchant. In `expt_b4` each of the 32 shards found the merchant's orders through `idx_orders_merchant_id`, read all of them from the table, and discarded all but the customer's. For merchant 1 that was 727 rows on 571 pages per shard, taking 8.9 ms to execute and 4.8 ms to plan.

With both columns in the index, each shard goes straight to the customer's orders, usually none or one.

- **T3 still runs on all 32 shards.** The index cuts the work per shard, not the number of tasks or their planning.
- **Measure:** T3's latency at 1 client (19.4 ms in `expt_b4`, 10.9 ms in `expt_b3` on faster nodes), and the T3 plan in `query-plans.log` (581 pages read per shard before).
- **Also watch T6.** T3 competes with T6 for the same workers, so T6 completed per second may rise (27.4 at 16 clients in `expt_b4`).

## Side effects

- **T1 maintains one more index**, on its insert into `orders` and on its final update of the total.
- **The load maintains one more index.** It was about 2 minutes per reload.
- **`idx_orders_merchant_id` becomes redundant**, since the new index starts with the same column. It is left in place here so this experiment changes one thing.

## 2. Plan capture after each run

In `expt_b4`, T6 slowed during a run under load: from 306 to 424 ms at 16 clients. The suspected cause is that T5 and T1 un-mark the pages they touch, so T6's index-only scan goes back to the table. The plan in `expt_b4` was captured before any benchmark and showed `Heap Fetches: 0`.

- **What to read:** `Heap Fetches` and the task's execution time for T6 in each `query-plans-after-c<clients>.log`, against `query-plans.log`.
- **It shows one shard of 32**, so it is a sample.
- **It does not affect the measurements.** It runs after pgbench has finished and before the next reload.
