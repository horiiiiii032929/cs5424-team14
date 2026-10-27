# expt_a14: VACUUM after load only (Kelvin, workload A; control for expt_a11)

Change: after every load, VACUUM (ANALYZE) on all six tables and CHECKPOINT on every node. Fillfactor is left at the default.

Why: the load's UPDATE of orders.total_amount leaves about 5M dead rows. This isolates the VACUUM part of expt_a11.

Base: expt_a0 plus the expt_a102 lookup indexes (sql/indexes.sql) and the expt_a102 correctness check after each measured run (sql/verify.sql -> validation.log). All folders also log HOT-update counters per measured run to benchmark-results/hot_updates.csv (measured outside the timed window). Compare against expt_a102.
