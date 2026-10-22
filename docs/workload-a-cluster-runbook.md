# Workload A cluster runbook

Updated 22 October 2026 after VPN reconnection. Both a115 full jobs are
[completely imported and audited](../results/cluster-full-a115-20261022/README.md).
Seven cases complete both phases, six with zero failures; both c64 warmups and
five measurements abort. All 12 validations and 26 runtime source-hash comparisons
pass. a112 remains provisional; the A pair must confirm the final tradeoff.

## Current deployment and jobs

The a114/a115 deployment is
`/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae`.
The experiments are merged into PR branch `codex/workload-a-followup` at `4caf234`;
PR #1 remains a draft and is not merged into `main`.

| Mode | Experiment / job | Recorded outcome |
|---|---|---|
| Scale-1 diagnostic | a114 / 979865 | Completed: 85.333 TPS; T6 764.5 ms; core and summary validation passed. |
| Scale-1 diagnostic | a115 / 979866 | Completed: 288.633 TPS; T6 115.9 ms; two retries, zero measured failures; validation passed. |
| Full, seed 42 | a115 / 979909 | COMPLETED 20 October 01:56:38; phase-eligible c1/c4/c8/c16 (c4 has one failure); c32/c64 measurements and c64 warmup abort; six validations passed. |
| Full, seed 7 | a115 / 979910 | COMPLETED 20 October 03:21:40; phase-eligible c1/c4/c32; c8/c16/c64 measurements and c64 warmup abort; six validations passed. |

## Reproduce the completed review

```sh
python3 scripts/review_a115_results.py results/cluster-full-a115-20261022
```

The audit verifies imported file hashes, runtime source, original protocols and
all command-line client counts, actual abort messages, raw success/failure/retry
and per-transaction counts, reset logs, source equivalence and all 12 validators.
`audit.json` keeps worker conflict excerpts and per-case phase details.
The importer now rejects missing warmup evidence rather than treating it as success,
and includes transaction/SQL source in future imports.

Do not rerun the import over the saved evidence. If another independent retrieval
is needed, use a fresh output directory and check the current queue first:

```sh
bash scripts/cluster-command.sh 'squeue -u cs14; sacct -j 979909,979910 --format=JobID,State,ExitCode,Elapsed,NodeList -X -P'
python3 scripts/import_cluster_jobs.py \
  /home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae \
  results/cluster-full-a115-independent-review \
  expt_a115:979909 expt_a115:979910
```

Slurm COMPLETED is insufficient: run.sh retains nonzero pgbench exits. A clean
comparison needs both phase exits zero; report failed records/retries even in
phase-complete cases. Seed-42 c4 has one serialization failure. Never certify a
case from summary TPS or passing post-run validation alone.

The complete audit is reflected in the A draft, status, results ledger, PR and
shared Docs. The existing matched figure still compares a0/a112; it contains no
excluded a115 cases. Final A selection remains with Kelvin/the A pair.

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
