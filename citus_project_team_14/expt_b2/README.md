# expt_b2 — Order items co-located with orders on `order_id`

Built on `expt_b1`. Not yet run.

| File | Where | Change |
| --- | --- | --- |
| `run.sh` | [line 444](run.sh#L444) | `create_distributed_table('order_items', 'order_id', colocate_with => 'orders')` |
| `run.sh` | [line 429](run.sh#L429) | Primary key becomes `(order_id, order_item_id)`. Citus requires the distribution column in every primary key. |

No transaction script changes. T3 already joins on `order_id`, and T1 already supplies `order_id` when it inserts order items.

Two consequences of the primary key change:

- It gives `order_items` an index that leads with `order_id`, which the join needs. Co-location and the index therefore arrive together.
- `order_item_id` is no longer unique on its own, only together with `order_id`.
