# Workload A follow-up runs

19 October 2026. New cluster work is blocked by SSH timing out before login.
No new jobs have been submitted by this follow-up. Job 965657 was run by Kelvin.

## Before submission

1. Connect to NUS VPN/network and check `bash scripts/cluster-command.sh 'squeue -u cs14'`.
2. Inspect `/home/stuproj/cs14/citus_project/expt_a102` and retrieve job 965657,
   including config, topology, source hashes, summary, transaction metrics,
   validation, PostgreSQL logs and Slurm output/error. Keep its exact source.
3. Check the current experiment directories and agree IDs with Kelvin.
   His update names a10/a11/a12/a14. New a109–a112 are provisional until checked.
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

Select the candidates supported by smoke/correctness results. For example:

```sh
bash scripts/submit_cluster.sh full expt_a0 expt_a102 expt_a111 expt_a112
```

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
