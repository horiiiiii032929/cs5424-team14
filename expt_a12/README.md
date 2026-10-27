# expt_a12: synchronous_commit=off on every node (Kelvin, workload A)

Change: synchronous_commit='off' in postgresql.conf on the coordinator and all workers.

Durability trade-off: a commit is acknowledged before its WAL reaches disk. A node crash can lose roughly the last 0.6 s (3 x wal_writer_delay) of acknowledged commits; the database stays consistent. Multi-shard transactions (T1, T7) use two-phase commit, so a crash could also lose one node's part of a transaction that was reported as committed. Not acceptable for real orders and stock.

Base: expt_a0 plus the expt_a102 lookup indexes (sql/indexes.sql) and the expt_a102 correctness check after each measured run (sql/verify.sql -> validation.log). All folders also log HOT-update counters per measured run to benchmark-results/hot_updates.csv (measured outside the timed window). Compare against expt_a102.
