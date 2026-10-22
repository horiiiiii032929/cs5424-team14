# Hikaru's five Task 2 designs

| Angle | Experiment | Implementation |
|---|---|---|
| Data placement | a101 | Five tables share merchant_id distribution; keys and joins include merchant_id. |
| Lookup indexes | a102 | orders(merchant_id,customer_id,created_at DESC), order_items(order_id), inventory(product_id). |
| Transaction execution | a103 | T1 uses one coordinator function call; pgbench retries serialization failures. |
| Repeated calculations | a104 | Exact daily sales totals, synchronously updated by T1, with raw reads for partial days. |
| Resource usage | a105/a106/a107 | Separately test work_mem=64MB and executor pool limits 2/8 against baseline 32MB/4. |
| Combination | a108 | Colocation, indexes, one-call T1 and exact sales summary. |
| Access-mode follow-up | a109/a110 | Add READ ONLY to T3/T4/T6 relative to a101/a108; isolation unchanged. |
| Join-key placement | a111 | Adapt Dessi's B b1/b2 placement to A on top of a102: inventory/product and item/order colocation. |
| Placement + access mode | a112 | Add READ ONLY to T3/T4/T6 relative to a111. |
| Safe read snapshots | a113 | Add DEFERRABLE to a112's read-only transactions, retaining SERIALIZABLE. |
| Striped summaries | a114 | a112 + exact daily sales totals in eight stripes per merchant/day. |
| Report-time index | a115 | a112 + only orders(created_at), controlling for a114's index. |

19 October: a109–a113 passed 151 new correctness checks. All seven follow-up
four-client local cases aborted, including original a101/a108 controls. These
local stress experiments do not establish a general concurrency fix. Subsequent
matched full runs support a112 as the provisional A design; a114's diagnostic
was slower. a115's full summaries show measured aborts; complete raw archive
review is pending after a renewed SSH timeout. B evidence is now archived separately.
See [current status](../docs/project-status.md). See [follow-up evidence](../results/followup-20261019/README.md).

The colocation variants now use exact COUNT(DISTINCT) global-ID validation after
measurement. The original GROUP BY validator spent over eleven minutes on the
scale-1 coordinator; the equivalent complete check took 25.753 seconds and passed
seven valid/corrupt-data regression checks. a102's original source stays unchanged.
Runtime source hashes distinguish older and revised validator versions.

No change is assumed to improve performance. Compare each individual version to
a0, then a108 to the components. Settings remain one-variable experiments; the
combined design keeps baseline memory/pool settings until evidence supports tuning.

## Correctness details

- **T1:** all inventory deductions, order rows and item rows are atomic. The
  function catches only business rejection (`no_data_found`); deadlocks and
  serialization failures reach pgbench. Duplicate products are processed in
  input order. Sequences remain on the coordinator and preserve globally unique
  generated IDs. No worker-delegated function is assumed to support these sequences.
- **Colocation:** primary keys include merchant_id as required by Citus.
  Globally unique IDs still come from the unchanged generator/coordinator
  sequences. This schema does not enforce cross-merchant uniqueness of manually
  supplied IDs. T5's ID-only access and T7's cross-merchant work retain their
  semantics; they may still touch multiple shards and must be included in results.
- **T3:** preserves the supplied SQL's `LIMIT 20` on joined rows. The brief says
  20 orders, which differs when an order has several items. This existing baseline
  discrepancy needs course clarification; an optimization must not quietly alter
  the meaning of the benchmark.
- **Sales totals:** initialized after every data reload, then updated inside the
  same successful T1 transaction. T5 only changes status; the report counts all
  statuses. Future delete/amount/time-changing transactions would also need
  summary maintenance. Full days use the summary; partial start/end days use
  base rows in the same statement snapshot. No asynchronous/stale cache is used.
- **Comparability:** keep A's nine weights, input/skew distributions, hardware,
  isolation, logging and data scale fixed within each environment. Count failures,
  report tail latency and investigate nonzero pgbench exits. pgbench TPS counts
  completed scripts, including expected business rollbacks; it is not an order
  acceptance rate. A stored-function rejection has no committed data changes.

## Sources

- [Citus data placement](https://docs.citusdata.com/en/stable/sharding/data_modeling.html)
- [Citus constraints](https://docs.citusdata.com/en/stable/develop/reference_ddl.html)
- [PostgreSQL multicolumn indexes](https://www.postgresql.org/docs/18/indexes-multicolumn.html)
- [Citus functions](https://docs.citusdata.com/en/stable/develop/api_udf.html#create-distributed-function)
- [Citus aggregation background](https://www.citusdata.com/blog/2018/06/14/scalable-incremental-data-aggregation/)
- [Citus executor settings](https://docs.citusdata.com/en/stable/develop/api_guc.html)
- [PostgreSQL memory settings](https://www.postgresql.org/docs/18/runtime-config-resource.html)
