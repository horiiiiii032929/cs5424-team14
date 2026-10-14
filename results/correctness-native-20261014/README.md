# Native distributed correctness verification

All **138 checks passed** on 14 October 2026 with PostgreSQL 18.6 / Citus 14.1.0, native ARM, one coordinator and four workers.

| Design | Checks passed |
|---|---:|
| expt_a0 | 22 |
| expt_a101 | 23 |
| expt_a103 | 24 |
| expt_a104 | 34 |
| expt_a108 | 35 |

Cases cover successful one/five-item orders, duplicate products, missing customers/products, rollback after later-item failures, two simultaneous orders competing for stock, inventory constraints, cross-merchant transfers, globally unique generated IDs, matching item/order totals, and summary-versus-raw report equivalence for 0/1/30/365 days.

The fixture is 10 merchants, 1,000 customers, 500 products, 500 initial orders and 1,500 initial items. Each folder contains source hashes, exact settings, fixture dimensions, pgbench output and check outcomes. Checks cover the supplied workload and listed edge cases; they do not prove correctness for arbitrary future transactions.
