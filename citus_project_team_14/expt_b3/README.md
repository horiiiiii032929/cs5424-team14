# expt_b3 — Covering index for T6

Built on `expt_b2`.

| File | Where | Change |
| --- | --- | --- |
| `run.sh` | [line 435](run.sh#L435) | `CREATE INDEX idx_orders_created_at_covering ON orders(created_at) INCLUDE (merchant_id, total_amount)` |
| `run.sh` | [line 498](run.sh#L498) | `VACUUM orders;` at the end of every data load, before `ANALYZE` |

No transaction script changes.

## Why both lines

T6 needs three columns of `orders`: `created_at` to filter, `merchant_id` to group and `total_amount` to sum. The index holds all three, so PostgreSQL can answer T6 from the index alone (an index-only scan) and read 8% of a small index instead of every row of the table.

An index-only scan is only allowed to skip the table for pages marked all-visible, and only `VACUUM` sets that mark. Straight after a load no page has it. Without the `VACUUM`, every index entry still costs a table lookup, and because the matching orders are spread over nearly every page, that is about as much work as the scan it replaces.

The `VACUUM` also removes the dead copy of every order that the load leaves behind when it fills in the totals.

## Side effects

- **The load gets slower.** There is one more index to maintain and a `VACUUM` at the end, 7 times per job. It was 2 minutes per reload in `expt_b2`.
- **T1's final update of `total_amount` now touches this index**, because `total_amount` is stored in it.
- **The benefit can wear off during a run.** T5 updates and T1 inserts un-mark the pages they touch. At `expt_b2`'s rate that is a few thousand pages out of roughly 100,000, but it grows with throughput.
