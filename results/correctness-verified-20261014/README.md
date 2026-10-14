# Distributed correctness verification

Run on 14 October 2026 using the isolated Docker Citus cluster.

| Design | Checks passed |
|---|---:|
| expt_a0 | 22 |
| expt_a101 | 23 |
| expt_a103 | 24 |
| expt_a104 | 34 |
| expt_a108 | 35 |

**138 checks passed.** Cases cover one/five-item orders, duplicate products, missing customers/products, rollback after a later-item failure, competing orders, nonnegative inventory, cross-merchant transfers, global ID uniqueness, matching item/order totals, and exact summary reports at 0/1/30/365 days.

The fixture is 10 merchants, 1,000 customers, 500 products, 500 initial orders and 1,500 initial items. Each folder records the fixture, source hashes, effective settings, pgbench output and Boolean check outcomes. PostgreSQL 18.4 / Citus 14.1.0, four workers, serializable isolation. This validates these cases; it is not a proof of correctness for arbitrary new transactions or a SoC performance result.
