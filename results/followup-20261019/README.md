# Workload A follow-up — 19 October 2026

**122 new correctness checks passed. All six four-client local stress cases
aborted. Neither read-only declarations nor the B-style placement adaptation
resolved these small-fixture benchmark failures. No new cluster jobs were submitted.**

## Evidence and attribution

- Kelvin's message, supplied by Hikaru in chat, reports cluster a102 job 965657
  unchanged from commit 82058e6, plus Kelvin's a10/a11/a12/a14 findings. The
  structured record is [kelvin-update.json](../team-update-20261019/kelvin-update.json).
  These are attributed reports, not independently checked raw measurements here.
- The preserved a0 job 918524 has 2.283 TPS at 64 clients; Kelvin reports a102 at
  3.40 TPS (approximately 48.9% higher). He reports passing validation and zero
  serialization failures. Retrieve his raw files before finalizing those claims.
- Dessi's B report in the shared Google Doc motivated the read-only test and
  pair-wise join colocation. The new variants explicitly credit that contribution.

## Correctness

| Variant | Parent / change | Checks |
|---|---|---:|
| a109 | a101 + T3/T4/T6 READ ONLY | 26 |
| a110 | a108 + T3/T4/T6 READ ONLY | 38 |
| a111 | a102 + inventory/product and item/order colocation | 29 |
| a112 | a111 + T3/T4/T6 READ ONLY | 29 |

Records: [read-only correctness](../correctness-readonly-20261019/) and
[join-placement correctness](../correctness-join-placement-20261019/).
The new tests exercise actual read scripts, cross-merchant transfers with distinct
inventory/product IDs, and actual distribution/colocation metadata. a112's
T3/T4/T6 EXPLAIN ANALYZE plans are retained on the small correctness fixture.

## Four-client local stress tests

All cases used the existing native ARM PostgreSQL 18.6 / Citus 14.1.0 Docker
image, one coordinator and four workers, SERIALIZABLE isolation, unchanged A
weights, seed 42, scale 0.01 and five-second warmup. The requested measurement
duration was increased to 45 seconds; warmup failures never started measurement.
Each case reloaded its own data. Tests ran serially. See the per-suite environment
record, fixture, effective settings and source hashes.

- [a101/a108/a109/a110](../readonly-pilot-20261019/SUMMARY.md): all aborted.
- [a111/a112](../join-placement-pilot-20261019/SUMMARY.md): both aborted in warmup.
- [Case status and post-failure checks](case-status.json): all 40 recorded
  post-failure invariants passed. This does not establish correctness for every
  possible schedule or resolve the client aborts.

Failed runs are retained with pgbench output, failure.json and worker diagnostics.
The generated comparisons leave their throughput and latency metrics blank.
No final design is selected from these results.

## What the diagnostics show

The logs show worker serialization failures followed by coordinator shard-commit
errors that abort pgbench clients despite --max-tries=3. Citus 14.1's
[placement_connection.c](https://github.com/citusdata/citus/blob/v14.1.0/src/backend/distributed/connection/placement_connection.c#L1004)
raises the matching shard-commit message without an explicit serialization SQLSTATE
at that site. This is consistent with the client aborts and supports investigating
the error propagation path; it does not identify a safe general retry policy.
Do not blanket-retry ambiguous distributed commit errors or modify the course
database binary to conceal the issue.

[PostgreSQL's pgbench documentation](https://www.postgresql.org/docs/18/pgbench.html#PGBENCH-ERRORS)
distinguishes retried serialization/deadlock failures from errors that abort a
client. [READ ONLY](https://www.postgresql.org/docs/18/sql-set-transaction.html)
is an access declaration, independent of isolation, and by itself does not promise
freedom from serialization failures. The original queries, isolation, durability
and retry limits were preserved in these variants.

The local fixture has ten merchants and one hot merchant, compared with 1,000
merchants and 100 hot merchants in the preserved scale-1 cluster baseline.
The distribution rules retain the same configured percentages, but the physical
contention and hardware differ. These negative local results do not prove that
a variant always fails on the course cluster, nor do they justify a speedup claim.

## Reproducibility and remaining work

`local_experiments.py` and `check_correctness.py` here snapshot the harness used
for the follow-up. a109/a110 do not enter the later join-placement-specific test
branch. The pilot environment's Git commit predates these uncommitted changes;
use the saved source hashes and the follow-up source commit for exact provenance.
Original a101/a102/a108 scripts and SQL were checked byte-for-byte against 82058e6.

The Slurm helper was checked with Bash 5 in Docker and stub sbatch/squeue commands:
selected experiments, xcnf constraint, smoke/full client matrices, existing-job
dependencies, sequential dependencies, and rejection before any submission for
an invalid experiment. These checks submitted no real jobs.

Both SSH inspections in this chat timed out before login. When NUS access is
available, inspect live folders/queue, retrieve a102 job 965657 and coordinate IDs
with Kelvin. Run diagnostic smoke cases before any full suite. The [runbook](../../docs/workload-a-cluster-runbook.md)
and [draft A report sections](../../docs/workload-a-report-draft.md) preserve the
next steps. The final design and scale-1 comparisons remain pending.
