# Workload A cluster runbook

Updated 20 October 2026. See [current project status](project-status.md) for
verified results and decisions. a112 remains provisional; a114 is not promoted.
a115's short diagnostic is promising, but its full results have not been imported.
SSH timed out before login at the latest reconciliation (16:55 Singapore time),
so current Slurm states are unknown. Check existing jobs before submitting more.

## Current deployment and jobs

The a114/a115 deployment is
`/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae`.
The experiments are merged into PR branch `codex/workload-a-followup` at `4caf234`;
PR #1 remains a draft and is not merged into `main`.

| Mode | Experiment / job | Recorded outcome |
|---|---|---|
| Scale-1 diagnostic | a114 / 979865 | Completed: 85.333 TPS; T6 764.5 ms; core and summary validation passed. |
| Scale-1 diagnostic | a115 / 979866 | Completed: 288.633 TPS; T6 115.9 ms; two retries, zero measured failures; validation passed. |
| Full, seed 42 | a115 / 979909 | Submitted on xcnf0–4; last saved checkpoint queued; current state/results unverified. |
| Full, seed 7 | a115 / 979910 | Submitted as the repeat on xcnf0–4; current state/results unverified. |

Do not infer completion from the earlier overnight finish estimate. Do not
resubmit these runs until their actual state and outputs have been inspected.

## Retrieve and review a115

Connect to NUS VPN/network if needed, then check the queue and accounting:

```sh
bash scripts/cluster-command.sh 'squeue -u cs14; sacct -j 979909,979910 --format=JobID,JobName,State,ExitCode,Elapsed,Start,End,NodeList -X -P'
```

After both jobs are finished and their output files are complete, retrieve them:

```sh
python3 scripts/import_cluster_jobs.py \
  /home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae \
  results/cluster-full-a115-20261020 \
  expt_a115:979909 expt_a115:979910
```

Use a new evidence directory if an earlier import already exists. Preserve all
attempts and partial failures. The importer streams saved outputs, hashes them
and builds `case-review.csv/json`; review its classifications against raw logs.
Slurm COMPLETED alone is insufficient: `run.sh` can retain a nonzero pgbench exit
while the job exits successfully.

Before using a case in the report, verify:

1. Same xcnf0 coordinator / xcnf1–4 workers, scale 1, six client counts
   (1/4/8/16/32/64), original weights, SERIALIZABLE, full logging, 60-second
   warmups, 600-second measurements, and data resets between counts.
2. Seeds 42 and 7, runtime source hashes, and a115's sole change from a112:
   `orders(created_at)` index. Check code against saved manifests.
3. All six warmup and measurement exit codes per job, expected/actual clients,
   retries, failed records, serialization/deadlock failures and worker logs.
4. Six complete passing post-run validations per job. Missing outputs or
   validations are unresolved evidence; integrity success does not erase aborts.
5. Compare completed scripts / 600 s with a0 977740 and a112 977773 plus eligible
   repeat cases from 978177. Its 64-client warmup exited 2 and remains excluded.

Only promote a115 after the full matrices support it and Kelvin reviews the
choice. Then update `docs/workload-a-report-draft.md`, the matched comparison
figure and its source data/contract, `results/README.md`, this runbook, the
project status, PR description and shared Google Docs. Until then the existing
matched figure correctly compares a0 and a112; it contains no a115 full results.

## Completed evidence

- Kelvin's a102/job 965657 and write-side runs: `results/cluster-import-20261019/`.
  a102/c16 warmup and a10/c32 measurement aborted; keep those flags.
- Initial smoke deployment: `~/citus_hikaru_20261019-165234_365eafd`.
  a102 passed; a101/a111/a112 aborted at four clients on the small fixture.
- Revised deployment: `~/citus_hikaru_20261019-172259_cf48c8d`.
  Scale-1 diagnostics a111/a112/a113 977617/977618/977619 passed. Matched full
  a0/a112 977740/977773 and a112 repeat 978177 are imported and reviewed in
  `results/cluster-full-20261019/`.
- a114 local correctness: 42 checks passed; its local four-client warmup aborted.
  Cluster diagnostics 979865/979866 are in `results/cluster-diagnostic-t6-20261020/`.
  a114's extra summary query work did not improve T6; do not rerun/promote it
  merely because the earlier preparation instructions proposed testing it.

## Additional experiments when needed

Reuse `~/pgsql`. Preserve the team's `~/citus_project`; upload committed files
into a fresh isolated directory with `bash scripts/upload_cluster.sh`.
Agree on experiment IDs and inspect all team jobs first. Port 5446 is shared;
the helper serializes jobs and waits for existing team work.

From the uploaded repository on xlogin, use focused selections:

```sh
bash scripts/submit_cluster.sh smoke expt_a115
BENCHMARK_NODELIST='xcnf[0-4]' bash scripts/submit_cluster.sh diagnostic expt_a115
# Only for a reviewed, necessary new comparison after checking the queue:
BENCHMARK_NODELIST='xcnf[0-4]' bash scripts/submit_cluster.sh full expt_a0 expt_a115
```

Smoke uses scale 0.01, one/four clients, 5 s warmup / 20 s measurement. Diagnostic
uses scale 1, four clients, 60 s warmup / 60 s measurement. Full restores the six
client counts and original 60 s / 600 s timings. Confirm actual node allocation
with Slurm; the helper passes `BENCHMARK_NODELIST` as `sbatch --nodelist`.
Preserve workload weights, isolation, retries, durability and log sampling.

The internal experiment cutoff is **23 October**. The report draft target is
**27 October**, packaging **29 October**, and target upload **30 October at 20:00
Singapore time**, before the official **23:59** deadline.
