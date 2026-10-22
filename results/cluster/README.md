# Course-cluster work — updated 22 October 2026

After VPN reconnection on 22 October, both a115 full jobs were completely
imported and audited. See [full evidence](../cluster-full-a115-20261022/README.md)
and [current status](../../docs/project-status.md). Earlier timeouts are historical;
raw evidence retrieval is no longer blocked. Existing team files and ~/pgsql
remain preserved; this review submitted no new jobs. Queue/accounting snapshots
are dated records, not continuing live-state guarantees.

## Verified existing experiments

[Kelvin's five original folders](../cluster-import-20261019/README.md) contain
30 measured cases. Twenty-eight completed both warmup and measurement; a10/c32
aborted in measurement and a102/c16 aborted in warmup. Their eligible TPS is
excluded from clean-run comparisons; original and partial figures remain separate.
Source, topology, settings, versions, raw logs and validation were reviewed.

## New runs

| Mode | Experiment / jobs | Outcome |
|---|---|---|
| Scale-0.01 smoke | a102 977432 | One/four clients completed; validation passed. |
| Scale-0.01 smoke | a101 977433; a111 977434; a112 977435 | One client completed; four-client warmup/measurement aborted. |
| Original scale-1 diagnostic | a101 977468 | Four-client warmup/measurement aborted; original validation was too slow. Independent exact validation passed; job then cancelled. |
| Original dependent diagnostics | a111 977469; a112 977470 | Cancelled before starting to replace the validator. |
| Revised scale-1 diagnostics | a111 977617; a112 977618; a113 977619 | All warmups/measurements completed; zero measured failures/retries; exact validation passed. |
| Full scale-1 matrix | a0 977740; a112 977773 | Both completed on xcnf0–4 with all six warmup and six measured exits per job zero. a0 3.2–3.6 TPS; a112 54.2–90.8 TPS, zero failed transactions, six passing validations. See [full results](../cluster-full-20261019/README.md). |
| Full repeat (pgbench seed 7) | a112 978177 | Completed; within 2.5% of seed 42, zero measured failures, six passing validations. 64-client warmup exit 2 (Citus-wrapped commit-time serialization conflict); flagged. Ledger `full-repeat-seed7-submission-20261019.tsv`. |
| T6 diagnostics | a114 979865; a115 979866 | Both clean. a114 (sales summaries) 85.3 TPS, T6 slower than a112; a115 (`orders(created_at)` index only) 288.6 TPS, T6 116 ms, two retried transactions and zero measured failures. See [T6 diagnostics](../cluster-diagnostic-t6-20261020/README.md). |
| Full matched a115 | 979909 (seed 42); 979910 (seed 7) | Both COMPLETED on 20 October on xcnf0–4; measured exits 2 at seed-42 c32/c64 and seed-7 c8/c16/c64. Complete archive/audit: 7 phase-eligible cases, 6 with zero failures; both c64 warmups abort; all 12 validations pass. Ledgers `t6-submissions-20261020.tsv`, `a115-repeat-seed7-submission-20261020.tsv`. |

The [smoke evidence](../cluster-smoke-20261019/README.md) and
[original diagnostic evidence](../cluster-diagnostic-original-20261019/README.md)
preserve outputs, source hashes and import manifests. All raw aborted TPS is
excluded from eligible performance comparisons. Completed Slurm status alone is
insufficient because run.sh preserves nonzero pgbench exits without failing the job.

## Validator repair

`validator-investigation/` preserves plans and activity showing the coordinator
aggregating millions of global-ID groups while the worker queries had finished.
The original validator remained active for over eleven minutes. An equivalent
exact COUNT(DISTINCT) uniqueness check, unchanged inventory/total checks, and
bounded post-run transaction completed in 25.753 seconds on the same full dataset.
Seven regression checks deliberately introduced duplicate global IDs and wrong
totals, verified rejection, and restored valid data.

This changes post-measurement validation, not benchmark transactions, weights,
isolation, retry policy, logging, memory settings or measured duration. Original
a102 source is unchanged. Updated colocation manifests identify the exact validator,
and each run's saved hashes identify its actual version.

Revised diagnostics use cf48c8d experiment source and the 4287182 submission
helper in `/home/stuproj/cs14/citus_hikaru_20261019-172259_cf48c8d`. They use scale 1,
four clients, original 60-second warmup, a 60-second measurement, and the fresh
initial data load (no redundant second load for this single client count).
See `revised-diagnostic-submission-20261019.txt` for job IDs. These are diagnostic
measurements, not the final six-client 600-second benchmark matrix.

All three revised diagnostics completed cleanly. Their configured-duration TPS
was 89.917/92.383/90.550 for a111/a112/a113; one 60-second observation per variant
does not establish a ranking. [Complete source and raw evidence](../cluster-diagnostic-20261019/README.md)
includes zero warmup/measurement exits and passing exact validation.

The completed full comparison tested a112 against a fresh original a0 control
on the same xcnf0–4 nodes, with six client counts, 60-second warmups, 600-second
measurements, data resets, seed 42, SERIALIZABLE and full logging. Pending
candidate 977741 was replaced before starting to correct its node request;
`full-node-pin-correction-20261019.json` and
`full-protocol-verification-20261019.json` retain the audit trail.
Both full jobs and repeat 978177 are imported and reviewed. a112 is provisional;
the repeat's 64-client warmup abort remains excluded from clean comparisons.

The a114/a115 diagnostics used
`/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae`. Full a115 jobs
979909/979910 finished there and are fully imported in the
[275-file archive](../cluster-full-a115-20261022/README.md). The source, command,
raw transaction/retry and validation audit is complete. Seven cases complete both
phases; six also have zero failed records. Excluded cases remain preserved.
a112 stays provisional pending Kelvin/the A pair's final decision.

B raw evidence and its separate source/protocol audit are preserved in
[the B review](../b-branch-review-20261022/README.md); it does not establish a
matched A/B comparison or a final B design.
