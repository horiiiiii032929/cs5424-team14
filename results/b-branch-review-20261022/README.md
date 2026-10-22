# Workload B branch import and review — 22 October 2026

Imported `desmond/expt_b0-6` at immutable commit
`5fa38157a7c1cb9abf1097e731f934a97a3db7c4`. All 975 source/output files are
preserved unchanged under `raw/expt_b0` through `raw/expt_b6`, including SQL,
run scripts, full transaction logs, worker logs, Slurm output, settings and plans.
This evidence copy does not overwrite the preserved submission baselines or
assert that the B pair has selected a final design. Final packaging must copy
reviewed experiment folders into `citus_project_team_14/`.

Reproduce the review:

```sh
python3 scripts/review_b_branch.py results/b-branch-review-20261022
```

[Case review](case-review.csv) contains all 42 cases. [Import manifest](import-manifest.json)
records SHA-256 checksums, equality to the pinned Git blobs, job protocols,
topologies and the seven b6 T6 checks. All 42 transaction-log line counts match
completed scripts plus failed log records. Import hashes establish file identity;
these B runs have no saved runtime source-hash manifest. Their source at execution
cannot independently be authenticated from the later Git snapshot.

## Phase completion and failures

Both warmup and measured pgbench exits must be zero. Missing exits are unresolved,
not successes. This eligibility check is separate from correctness, retry counts,
transaction failures, and matched hardware.

| Experiment | Job | Both phases completed at clients | Excluded client counts |
|---|---:|---|---|
| b0 | 918781 | 1, 4, 32 | 8/16 measured abort; 64 warmup abort |
| b1 | 928267 | 1, 4, 8 | 16 measured abort; 32/64 warmup abort |
| b2 | 928583 | 1, 4, 8, 16 | 32 warmup abort; 64 measured abort |
| b3 | 929009 | 1 | 4 measured abort; 8/16/32/64 both phases abort |
| b4 | 931181 | 1, 4, 8, 16 | 32/64 measured abort |
| b5 | 931635 | 1, 4, 8, 16 | 32 measured abort; 64 both phases abort |
| b6 | 956803 | 1, 4, 16 | 8 warmup abort; 32/64 both phases abort |

b0 also records 10 and 340 failed transactions at its phase-complete c4/c32;
only b0/c1 is phase-complete with zero measured failures. Other experiments'
phase-complete cases have zero failed log records. Thus 22/42 cases complete
both phases, and 20/42 also have zero failed log records. No B experiment has
an eligible 64-client comparison under this policy.

## b6 findings

| Clients | Raw scripts / 600 s TPS | Warmup / measured exit | Interpretation |
|---:|---:|---|---|
| 1 | 114.445 | 0 / 0 | Phase-complete; no measured failures |
| 4 | 327.505 | 0 / 0 | Phase-complete; no measured failures |
| 8 | 518.922 | 2 / 0 | Exclude: aborted warmup |
| 16 | 539.437 | 0 / 0 | Phase-complete; no measured failures; 176 retried transactions / 186 retries |
| 32 | 507.667 | 2 / 2 | Exclude: aborted warmup and measurement |
| 64 | 483.525 | 2 / 2 | Exclude: aborted warmup and measurement |

The shared report's 539 TPS at 16 clients is supported by raw output and zero
phase exits. Its 483.53 TPS at 64 clients is an incomplete-run observation;
it cannot support a clean 50% gain over b5, which also aborted at 64 clients.
Tables at 64 clients for b0–b6 must retain their values only as flagged diagnostics,
with no clean speedup claim. A zero `failed_log_records` value does not negate a
client abort: b6/c32 and c64 record zero failed transaction rows but exit 2.

b6's seven saved T6 checks (initial and after each client count) each compare
1,000 merchants in both directions with EXCEPT and report zero differences.
This supports equivalence for those snapshots. It is not a general integrity or
concurrency proof: no saved core stock/order/global-ID validator is present.
The checks are diagnostic (`capture_plans ... || true`), not fail-fast assertions.

## Source and protocol review

- b1 colocates inventory with products by product_id and adds the selected product
  IDs to T7 update predicates. T7 still looks up and uses actual inventory IDs;
  the routing change need not assume inventory_id equals product_id.
- b2 colocates order_items with orders by order_id.
- b3 adds orders(created_at) INCLUDE (merchant_id, total_amount) and VACUUM.
- b4 adds READ ONLY to T3/T4/T6, coordinator-resolved T6 timestamps, and plan capture.
  This is not an isolated test of READ ONLY alone and does not resolve all aborts.
- b5 adds orders(merchant_id, customer_id) and post-measurement plan capture.
- b6 adds a reference-table daily rollup and coordinator cutoff table; only
  history before the load-date cutoff is precomputed. T1 adds current orders;
  T5 changes status, not historical totals. T6 combines historical whole days
  with raw boundary/tail rows. This avoids synchronously maintaining the
  historical reference table during timed writes, unlike A's a114 design.

The saved configurations use scale 1, seed 42, SERIALIZABLE, 60 s warmup,
600 s measurements, full log sampling, data resets between counts, four workers,
and B weights 10/10/5/5/10/10/30/10/10. Versions record PostgreSQL 18.6/Citus 14.1.0.
Hardware is not matched across the series: b0/b2/b3/b5 use xcnf8–12, b1 uses
xcnc36–40, b4 uses xcne6/xcne7 and xcnf0–2, and b6 uses xcnf10–14. b5 and b6 therefore differ in
node allocation as well as SQL. Do not attribute their entire throughput change
to the rollup or make a statistical confidence claim from one seed.

## Remaining team decisions

The report’s supplementary T7-only figures are not present in this b0–b6
snapshot and remain teammate-reported.

The B pair must confirm attribution and final selection. Review the flagged
matrices, retain failure counts, and decide whether a necessary matched repeat
and additional core correctness evidence can be completed before the 23 October
cutoff. No new benchmark jobs were submitted by this review.
