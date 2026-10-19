# a113 correctness — 19 October 2026

All 29 checks passed on native ARM PostgreSQL 18.6/Citus 14.1.0 with one
coordinator and four workers. a113 differs from a112 only by changing T3/T4/T6
to BEGIN READ ONLY DEFERRABLE. It retains SERIALIZABLE isolation, the query
bodies, write transactions, retry limit and workload weights.

The checks exercise successful/rejected orders, rollback, competing orders,
inventory constraints, transfers with distinct inventory and product IDs,
actual placement metadata, and the real read scripts. Exact source hashes,
fixture dimensions, settings and outputs are retained in expt_a113/.

The separate four-client pilot aborted in warmup, including a T2 shard-commit
error. All five post-failure integrity checks passed. Correctness-test success
does not establish concurrency robustness or a performance gain.

Sources for the hypothesis:
[PostgreSQL SET TRANSACTION](https://www.postgresql.org/docs/18/sql-set-transaction.html)
and [Citus 14.1 remote BEGIN construction](https://github.com/citusdata/citus/blob/v14.1.0/src/backend/distributed/transaction/remote_transaction.c#L374).
