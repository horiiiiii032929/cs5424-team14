# expt_a10: autocommit single-statement updates (Kelvin, workload A)

Change: removed BEGIN/COMMIT from T2, T5, T8 and T9, so each runs as one autocommit UPDATE. The SQL statements themselves are unchanged (T2 keeps its stock check in the WHERE clause).

Why: one client round trip instead of three, and no separate COMMIT at which Citus can report a serialization failure as the non-retryable "could not commit transaction for shard".

Base: expt_a0 plus the expt_a102 lookup indexes (sql/indexes.sql) and the expt_a102 correctness check after each measured run (sql/verify.sql -> validation.log). All folders also log HOT-update counters per measured run to benchmark-results/hot_updates.csv (measured outside the timed window). Compare against expt_a102.
