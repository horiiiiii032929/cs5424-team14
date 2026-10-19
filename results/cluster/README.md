# Course-cluster work — 19 October 2026

SSH access is restored. Existing team files and ~/pgsql were preserved; new jobs
use isolated deployment directories and xcnf nodes. The team queue was empty at
the first successful inspection. All submissions serialize on the shared team port.

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
| Full scale-1 matrix | a0 977740; a112 977773 | Baseline running; candidate queued after it, explicitly requesting the same xcnf0–4 nodes. Results pending. |

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

The full comparison advances a112 against a fresh original a0 control. It restores
all six client counts, 60-second warmups, 600-second measurements, per-count
data resets, seed 42, SERIALIZABLE isolation and full log sampling. Baseline
977740 is running on xcnf0–4. Candidate 977773 explicitly requests those nodes
and depends on the baseline. Pending candidate 977741 was cancelled and replaced
before starting because the initial environment-variable node request was not
recognized; `full-node-pin-correction-20261019.json` preserves the correction.
`full-protocol-verification-20261019.json` records the checked baseline settings
and candidate Slurm node request. No full performance results or final A winner
are claimed. Review every phase, validation and failure log, then assess repeats.
