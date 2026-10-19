# expt_a11: fillfactor 80 + VACUUM after load (Kelvin, workload A)

Change: customers, products, inventory and orders are created WITH (fillfactor=80) before the data load. After every load: VACUUM (ANALYZE) on all six tables and CHECKPOINT on every node. No indexes on updated columns. schema-create.log records one shard's reloptions per table.

Why: free space on each page lets UPDATEs of unindexed columns be HOT. Compare with expt_a14 (VACUUM only) to separate the two effects.

Base: expt_a0 plus the expt_a102 lookup indexes (sql/indexes.sql) and the expt_a102 correctness check after each measured run (sql/verify.sql -> validation.log). All folders also log HOT-update counters per measured run to benchmark-results/hot_updates.csv (measured outside the timed window). Compare against expt_a102.
