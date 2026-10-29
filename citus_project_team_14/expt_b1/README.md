# expt_b1 — Inventory co-located with products on `product_id`


| File | Where | Change |
| --- | --- | --- |
| `run.sh` | [line 442](run.sh#L442) | `create_distributed_table('inventory', 'product_id', colocate_with => 'products')` |
| `run.sh` | [line 427](run.sh#L427) | Primary key becomes `(product_id, inventory_id)`. Citus requires the distribution column in every primary key. |
| `T7_inventory_transfer.sql` | [lines 53](transactions/T7_inventory_transfer.sql#L53) and [65](transactions/T7_inventory_transfer.sql#L65) | Add `AND product_id = ...` to both updates. They filter on `inventory_id` only, which would no longer route. |

Two consequences of the primary key change:

- It gives `inventory` an index that leads with `product_id`. Routing and the index therefore arrive together and this experiment cannot separate them.
- `inventory_id` is no longer unique on its own, only together with `product_id`.
