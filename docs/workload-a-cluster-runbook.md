# Workload A follow-up runs

19 October 2026. SSH access is restored. Kelvin's job 965657 and write-side
experiments have been retrieved and reviewed. The isolated deployment is
`/home/stuproj/cs14/citus_hikaru_20261019-165234_365eafd`.
Smoke jobs 977432–977435 ran on xcnf0–4. a102 passed at one/four clients;
a101/a111/a112 passed at one client and aborted at four. Preserve those failures.
The revised deployment is `/home/stuproj/cs14/citus_hikaru_20261019-172259_cf48c8d`.
Scale-1 diagnostics a111/a112/a113 (977617/977618/977619) completed cleanly,
including exact validation. Full control a0 977740 and candidate a112 977773
completed on xcnf0–4 (see `results/cluster-full-20261019/`). Repeat a112 978177
uses PGBENCH_SEED=7 on the same nodes and completed (64-client warmup abort flagged).
20 October: a114/a115 deployed to `/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae`.
Diagnostics 979865 (a114) and 979866 (a115) completed; see
`results/cluster-diagnostic-t6-20261020/`. Full a115 runs 979909 (seed 42) and
979910 (seed 7) are queued on xcnf0–4; do not resubmit while they are active.
Import finished jobs with
`python3 scripts/import_cluster_jobs.py <deployment> <out_dir> expt_aN:JOB ...`.

## Before submission

1. Connect to NUS VPN/network and check `bash scripts/cluster-command.sh 'squeue -u cs14'`.
2. Inspect `/home/stuproj/cs14/citus_project/expt_a102` and retrieve job 965657,
   including config, topology, source hashes, summary, transaction metrics,
   validation, PostgreSQL logs and Slurm output/error. Keep its exact source.
3. Check the current experiment directories and agree IDs with Kelvin.
   His update names a10/a11/a12/a14. At the successful inspection a109–a113
   were unused in the shared project; our copies use isolated directories.
4. Upload committed files into a fresh directory using `bash scripts/upload_cluster.sh`.
   Reuse ~/pgsql and preserve Dessi's ~/citus_project. Do not run the installer.

## Focused smoke comparison

Run on xlogin from the isolated uploaded repository:

```sh
bash scripts/submit_cluster.sh smoke expt_a102 expt_a111 expt_a112
```

The helper selects xcnf hardware, waits for existing team jobs, and serializes
its own jobs because team port 5446 is shared. Smoke runs cover one and four
clients, scale 0.01, five-second warmup and 20-second measurements. Do not submit
independent jobs in parallel with another teammate's suite.

Review pgbench exit codes, expected/actual clients, validation.log and worker
logs. Slurm COMPLETED alone is insufficient: run.sh can preserve a pgbench
failure while still exiting successfully. Treat an aborted run as failed and
retain diagnostics. A read-only declaration is a hypothesis, not a guaranteed fix.
The local four-client runs for a101/a108/a109/a110 all aborted, so prioritize
the narrower join-key placement in a111/a112. Retain the failed variants as
evidence; reproduce them on the cluster only when useful to the diagnosis.

## Full comparison after reviewing smoke results

Before full runs, distinguish the scale-0.01 contention result from the course
data size with a short four-client diagnostic:

```sh
bash scripts/submit_cluster.sh diagnostic expt_a111 expt_a112 expt_a113
```

This uses scale 1 and the original 60-second warmup, followed by a 60-second
measurement at four clients. It is a diagnostic, not the final 600-second result.
It uses the fresh initial load and skips a redundant reload for this single
client count. Smoke/full matrices retain their original reset behavior.
Do not promote a design with an aborted diagnostic into a full performance claim.

### a114 diagnostic (prepared, not submitted)

a114 is a112 plus a104's exact daily sales summaries, targeting T6, which is
67–83% of a112's recorded time in the matched full run. T1 upserts the order into
one of eight per-merchant/day stripes (`order_id % 8`) just before COMMIT; T6
sums the stripes for whole days and reads raw orders only for the two partial-day
ranges (a104's T6 index-scanned the whole window), still under READ ONLY.
Isolation, weights, retries and durability are unchanged. Locally at 1M orders the
original query with only a104's `orders(created_at)` index was faster than either
summary T6 (`results/t6-plan-check-20261019/`), so credit the summary itself only
against an "a112 + created_at index" control.
Correctness and the local pilot are in `results/correctness-summary-20261019/`
and `results/summary-pilot-20261019/` (branch `expt-a114-sales-summary`):
42/42 checks passed; the local pilot completed at one client and aborted at four
in warmup with the same commit-time SSI error as a112, after more T1
serialization failures than a112 (63 vs 32). Watch T1 retries in the diagnostic.

Upload a commit that contains `expt_a114` with `bash scripts/upload_cluster.sh`,
then from that new directory on xlogin:

```sh
BENCHMARK_NODELIST='xcnf[0-4]' bash scripts/submit_cluster.sh diagnostic expt_a114
```

Compare it with a112 diagnostic 977618 (same scale-1, four-client, 60 s + 60 s
settings on xcnf0–4). The helper waits for existing team jobs such as the seed-7
a112 repeat 978177. Check pgbench exits, serialization failures/retries, and
that validation.log contains both `core invariants passed` and `striped sales
summary matches base orders`. Promote a114 to a full matched run only if the
diagnostic is clean and T6 latency drops:
`BENCHMARK_NODELIST='xcnf[0-4]' bash scripts/submit_cluster.sh full expt_a114`.

Select the candidates supported by smoke/correctness results. For example:

```sh
bash scripts/submit_cluster.sh full expt_a0 expt_a102 expt_a111 expt_a112
```

For a matched hardware comparison, explicitly pin the same five nodes with
`BENCHMARK_NODELIST='xcnf[0-4]' bash scripts/submit_cluster.sh full expt_a0 expt_a112`.
The helper passes this as sbatch's --nodelist option. Confirm ReqNodeList/NodeList
with scontrol rather than relying on an assumed Slurm environment-variable name.

Use the listed full matrix only if all of those comparisons remain useful after
review. Fresh matched a0/a102 controls are useful when topology or environment
differs from Kelvin's existing run; do not rerun them merely to duplicate evidence.
Full runs explicitly set scale 1, 60-second warmup, 600-second measurements and
1/4/8/16/32/64 clients. Preserve original weights, SERIALIZABLE isolation,
durability and full logging. Test at least two recorded seeds for the strongest
eligible designs; use fresh job IDs and preserve all attempts.

The submitter does not automatically promote smoke results into full runs.
Save every submissions ledger and match report experiment IDs to result folders.
23 October is the internal experiment cutoff. Draft A report text is in
`docs/workload-a-report-draft.md`; measurements remain provisional until reviewed.
