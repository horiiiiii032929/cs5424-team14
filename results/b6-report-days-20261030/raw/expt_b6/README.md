# expt_b6 — Daily sales rollup for T6

Built on `expt_b5`. Not yet run.

| # | File | Where | Change |
| --- | --- | --- | --- |
| 1 | `run.sh` | [lines 438 to 441](run.sh#L438-L441), [452](run.sh#L452) | New table `merchant_daily_sales` (order count and revenue per merchant per day), a reference table. New one-row table `merchant_daily_sales_cutoff`, local to the coordinator. |
| 2 | `run.sh` | [lines 505 to 514](run.sh#L505-L514) | At the end of every load: record today's date as the cutoff, fill `merchant_daily_sales` for every day before it, and `VACUUM` it. Both tables are added to the `TRUNCATE` at [line 473](run.sh#L473). |
| 3 | `T6_global_sales.sql` | whole file | T6 reads whole days from `merchant_daily_sales` and only the rest of its window from `orders`. |
| 4 | `run.sh` | [lines 536 to 543](run.sh#L536-L543) | The plan capture now shows the new T6, and checks that it returns the same per-merchant totals as the old query. |

No other transaction changes.

## Why

T6 is 65.7% of all time in `expt_b5`, and by estimate its 32 shard tasks use nearly all 16 worker cores. Each call reads and groups about 410,000 orders, almost all of them in days that cannot change during a run.

## Why the rollup stays correct without being updated

- **T1 only inserts orders stamped `CURRENT_TIMESTAMP`**, which is on or after the cutoff. Its final update changes only the order it just created.
- **T5 only changes `order_status`**, which T6 does not read.
- **No transaction deletes orders** or changes `created_at`, `merchant_id` or `total_amount` on an existing one.
- **The data is reloaded and the rollup rebuilt before every client count.**

So every day before the cutoff is frozen once the load finishes, and T1 does not need to touch the rollup.

## How T6 splits its window

T6's first statement reads the clock and the cutoff, and splits `[now - 30 days, now)` into three parts that cover it exactly:

| Part | Range | Read from |
| --- | --- | --- |
| Partial first day | window start up to the next midnight | `orders` |
| Whole days | that midnight up to the cutoff | `merchant_daily_sales` |
| Since the cutoff | the cutoff up to now | `orders` |

The second statement adds the three parts per merchant, then sorts and keeps the top 20 as before.

- **The two `orders` parts are separate ranges**, so each can still use the covering index without visiting the table.
- **Every part is grouped by merchant before the parts are combined**, so at most 1,000 rows leave each part. See "Short test job" below for why.
- **If the window ever started after the cutoff**, the whole-days part would be empty and the last part would start at the window's first midnight instead. That cannot happen here, because the data is reloaded before each client count; it is handled so the split stays exact.
- **A job that runs past midnight stays correct.** The "since the cutoff" part just grows by a day.

## Expected effect (estimates, not measured)

- **Rows read per T6:** about 29,000 rollup rows on one worker, plus about 1,000 orders per shard instead of 13,500.
- **Worker CPU per T6:** roughly 0.13 s instead of 0.4 to 0.6 s.
- **T6 should stop slowing down during a run.** The pages T5 dirties are almost all in old days, which T6 no longer reads from `orders`.

## Side effects

- **The load does one more aggregate** over all 5M orders and inserts about 364,000 rows into a reference table.
- **T6 now reaches 32 shards twice**, once for each `orders` part, so 64 small tasks instead of 32 large ones.

## What to check

- **`query-plans.log` and each `query-plans-after-c<clients>.log`, the "T6 check" line:** `only_in_old` and `only_in_new` must both be 0. It compares all 1,000 per-merchant totals, not the top 20, because merchants tied at 20th place could come out in either order.
- **The T6 plan:** how Citus combines the reference table with the two 32-shard parts. I expect each part to be computed separately and added up at the end, but have not confirmed it.
- **Whether pre-computed totals are acceptable** for the project. T6 still returns exactly what its description asks for.

## Short test job (956534)

Run before the full job, from `query-plans.log`.

- **The rollup gives the right answer.** The T6 check found all 1,000 merchants with identical totals: `only_in_old = 0`, `only_in_new = 0`.
- **Citus runs T6 in four steps:**
  1. The partial first day, as 32 tasks. It returned 0 rows, as expected.
  2. The part since the cutoff, as 32 tasks of about 470 rows each, about 1 ms per task.
  3. A single task on one worker that reads the rollup and adds the two results above. The rollup read was an index-only scan of 28,990 rows taking 8 ms.
  4. The final grouping and top 20, on the coordinator.
- **The first version shipped every rollup row to the coordinator.** The rollup part was not grouped, so step 3 sent 29,990 rows (875 kB) back, and the coordinator grouped them in step 4. Step 3 took 120 ms and step 4 took 28 ms, out of 177 to 198 ms in total. That is slower at 1 client than the old T6, which took 74 to 76 ms in `expt_b5`'s capture.
- **Fixed before the full run:** the rollup part now groups by merchant itself, so step 3 returns at most 2,000 rows.
- **A second short job (956642) failed at the first T6** because that fix left the grouped rollup part without column names: `column "order_count" does not exist`. Fixed by naming them. The loader itself worked: 363,836 rollup rows, and a reload took 2 min 14 s against 2 min 6 s in `expt_b5`.
- **Worker work is already far smaller.** Steps 1 to 3 add up to roughly 60 ms of worker time per T6 at the start of a run, against roughly 400 to 470 ms for the old T6. This is an estimate from the plan's task times.
- **Steps 1 and 2 send their results to all 4 workers**, because Citus does not know in advance which worker will run step 3. They are small (up to 43 kB each).
