# a114 local pilot — 19 October 2026

**Local Docker pilot, not a course-cluster result.** Native ARM PostgreSQL 18.6 /
Citus 14.1.0, one coordinator and four workers, scale 0.01 (10 merchants, one hot),
SERIALIZABLE, original A weights, --max-tries=3, seed 42, 5 s warmup, 45 s
measurement, fresh data per case. a112 ran in the same suite as the matched control.
Generated table: [SUMMARY.md](SUMMARY.md); raw data in each case folder.

| Case | Outcome | TPS | T1 mean ms | T6 mean ms | Checks |
|---|---|---:|---:|---:|---|
| a112 c1 | completed | 306.25 | 5.86 | 5.56 | passed |
| a114 c1 | completed | 285.28 | 6.13 | 8.74 | passed (incl. exact summary + T6 at 0/1/30/365 days) |
| a112 c4 | **aborted in warmup** | NA | NA | NA | 5/5 post-failure checks passed |
| a114 c4 | **aborted in warmup** | NA | NA | NA | 10/10 post-failure checks passed |

Both four-client cases aborted the same way as every earlier local four-client
run: worker SSI "pivot" failures at commit surface as the coordinator error
"could not commit transaction for shard … on at least one active node", which
pgbench does not retry. Failures are preserved (`*/c4/failure.json`, `warmup.txt`).

In the 5 s warmups before the abort, a114's T1 had 63 serialization failures that
exhausted three tries (7.0% of T1) and 29.3% retried, versus 32 (3.4%) and 24.8%
for a112. The eight-stripe summary did not remove extra T1 conflicts on this
10-merchant fixture. One short warmup is not a stable rate.

At this size a114 is ~7% slower at one client: the summary T6 adds Citus subplan
round trips that cost more than the 50k-order scan it avoids. The larger
[T6 plan check](../t6-plan-check-20261019/README.md) (1M orders) shows the
summary T6 at 25.5 ms vs 78.0 ms for a112's query. Only the scale-1 cluster
diagnostic can say whether a114 helps; see the runbook for the prepared command.

Command: `python3 scripts/local_experiments.py --experiments expt_a112 expt_a114
--clients 1 4 --duration 45 --output results/summary-pilot-20261019 --continue-on-error`.
environment.json's git_commit is the parent commit; the a114 sources were
uncommitted at run time and are pinned by each case's `code-sha256.json`.
