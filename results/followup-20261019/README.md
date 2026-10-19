# Workload A follow-up — 19 October 2026

**151 follow-up correctness checks passed across a109–a113. All seven four-client
local stress cases aborted. Read-only declarations, DEFERRABLE and B-style
placement did not resolve those local failures.**

SSH access was later restored. Kelvin's raw results are now reviewed, the course
smoke suite is complete, and scale-1 diagnostics are recorded in
[cluster work](../cluster/README.md). a102/c16 had an aborted warmup despite its
completed measurement; that observation is excluded from clean-run comparisons.

## Evidence and attribution

- Kelvin's message, supplied by Hikaru in chat, reports cluster a102 job 965657
  unchanged from commit 82058e6, plus Kelvin's a10/a11/a12/a14 findings. The
  structured record is [kelvin-update.json](../team-update-20261019/kelvin-update.json).
  This is the original attributed message; the later [raw import](../cluster-import-20261019/README.md)
  independently verifies and qualifies its claims.
- The preserved a0 job 918524 has 2.283 TPS at 64 clients; Kelvin reports a102 at
  3.40 TPS (approximately 48.9% higher). Retrieved raw files record 3.398 TPS,
  all six completed measurements and validation, but an aborted 16-client warmup.
- Dessi's B report in the shared Google Doc motivated the read-only test and
  pair-wise join colocation. The new variants explicitly credit that contribution.

## Correctness

| Variant | Parent / change | Checks |
|---|---|---:|
| a109 | a101 + T3/T4/T6 READ ONLY | 26 |
| a110 | a108 + T3/T4/T6 READ ONLY | 38 |
| a111 | a102 + inventory/product and item/order colocation | 29 |
| a112 | a111 + T3/T4/T6 READ ONLY | 29 |
| a113 | a112 + READ ONLY DEFERRABLE | 29 |

Records: [read-only correctness](../correctness-readonly-20261019/) and
[join-placement correctness](../correctness-join-placement-20261019/).
The separate [a113 record](../correctness-deferrable-20261019/README.md) adds 29 checks.
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
- [a113](../deferrable-pilot-20261019/README.md): aborted in warmup; all five
  post-failure checks passed, in addition to the 40 original follow-up checks.
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
Original a101/a102/a108 benchmark scripts and transaction SQL were checked
against 82058e6. Later changes replace only the post-run validator for colocation
variants; runtime hashes distinguish the versions. a102's original source is unchanged.

The Slurm helper was checked with Bash 5 in Docker and stub sbatch/squeue commands:
selected experiments, xcnf constraint, smoke/full client matrices, existing-job
dependencies, sequential dependencies, and rejection before any submission for
an invalid experiment. These checks submitted no real jobs.

Initial SSH inspections timed out; access was later restored. a102 job 965657
and Kelvin's four write-side variants were retrieved. Smoke tests reproduced
the concurrent failure, so revised scale-1 diagnostics are running before any
full suite. The [runbook](../../docs/workload-a-cluster-runbook.md)
and [draft A report sections](../../docs/workload-a-report-draft.md) preserve the
next steps. The final design and scale-1 comparisons remain pending.
