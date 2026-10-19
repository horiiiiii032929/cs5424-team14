# CS5424 / CS4224 — Team 14

Team: Hikaru, Kelvin, Dessi and Xincheng. Team account: `cs14`.
Submission deadline: **30 October 2026, 23:59 Singapore time**.

This repository holds Dessi's preserved A/B baseline snapshots and Hikaru's
implementations of five proposed Task 2 designs. The proposed work split is
Hikaru + Kelvin on A and Dessi + Xincheng on B.

**19 October status:** SSH is restored and Kelvin's a102/job 965657 plus write-side
results have been retrieved and reviewed. a102 completed all six measurements,
but its 16-client warmup aborted; that case is flagged. Clean concurrent cases
show 49–57% observed gains over the preserved a0 job, but only −3% to +6% over a
fresh a0 control on matched-family nodes. The original correctness suite passed 138
checks; a109–a113 passed 151 follow-up checks. Their local concurrency failures
remain unresolved. On the cluster, a102 smoke passed; a101/a111/a112 aborted at
four clients. After the validator repair, scale-1 diagnostics for a111/a112/a113
completed cleanly at 89.9/92.4/90.6 TPS. The matched full comparison on xcnf0–4
then completed cleanly: a112 ran 54.2–90.8 TPS versus 3.2–3.6 TPS for fresh a0
(17–28×), with zero failed transactions and passing validation at all six client
counts ([full results](results/cluster-full-20261019/README.md)). a112 is the
provisional A selection; a seed-7 repeat (job 978177) is running.
See [cluster evidence](results/cluster/README.md).
See [results and next steps](results/README.md), the [A report draft](docs/workload-a-report-draft.md)
and [cluster runbook](docs/workload-a-cluster-runbook.md).

## Start here

- [Experiments](citus_project_team_14/README.md): complete Slurm scripts and SQL.
- [Results](results/README.md): measured results and their limitations.
- [Google Drive documents](GOOGLE_DRIVE_PROJECT.md): team plan and assignment guides.
- [Cluster access](CLUSTER_SETUP.md): private `.env` setup and SSH.
- [Implementation notes](optimizations/README.md): what changes and how to compare.
- [AI usage record](AI_USAGE.md): implementation assistance to declare in submission.

## Run the local distributed checks

Requires Docker Compose and Python 3. The test cluster contains one coordinator
and four Citus workers. It exposes no host ports and uses only its own containers.

```sh
python3 scripts/build_experiments.py
python3 scripts/check_correctness.py --output results/my-correctness-run
python3 scripts/local_experiments.py --output results/my-local-pilot --continue-on-error
python3 scripts/summarize_results.py results/my-local-pilot
docker compose down
```

The local pilot uses scale 0.01, 5-second warmup and 20-second measurements.
It is a quick implementation check, not a substitute for the course's scale-1
Slurm results. The native ARM fixture builds Citus 14.1.0 from a checksum-verified
source archive on a pinned PostgreSQL 18.6 image. First startup builds the image.
It was prepared for this Apple Silicon Mac; use the Slurm scripts for the course
cluster. Full raw pilot logs are retained.
`--continue-on-error` preserves a `failure.json` for failed warmups/measurements
and continues the matrix. The report labels those cases FAILED and excludes their
throughput from ranking.

## Run on the course cluster

Clone or copy this repository into a **separate directory** from Dessi's existing
`~/citus_project`. Reuse `~/pgsql`; do not rerun the destructive installer.
Check the live experiment folders with teammates before adopting a101–a108.
From the Mac, `bash scripts/upload_cluster.sh` sends the committed files to a new
isolated directory without putting GitHub credentials on the shared cluster account.

```sh
# On xlogin, from this repo. Smoke-test first, inspect results, then full suite.
bash scripts/submit_cluster.sh smoke
# After the smoke jobs complete successfully:
bash scripts/submit_cluster.sh full
```

The submitter serializes jobs because all team jobs use port 5446. It also waits
for existing team jobs. Coordinate with teammates before anyone submits further
jobs independently. It pins xcnf hardware; smoke runs include 1 and 4 clients.
Pass explicit experiment IDs after smoke/full to submit a focused selection.
The full suite retains the original six client counts,
600-second runs, 60-second warmup, workload mix, isolation and full log sampling.
Use job IDs in each folder to distinguish smoke from full runs.
Inspect `summary.csv`'s `pgbench_exit_code`, retry/failure counts and `validation.log`;
Slurm COMPLETED alone does not mean every measured client count succeeded.

## Work together

The repository is public. Anyone can view and clone it:

```sh
git clone https://github.com/horiiiiii032929/cs5424-team14.git
cd cs5424-team14
git switch -c your-name/your-optimization
```

Teammates can fork the repository and open pull requests. Direct push access
requires a collaborator invitation using their GitHub usernames.

Use separate experiment folders, preserve `expt_a0`/`expt_b0`, record settings and
results, and open a pull request. Never commit `.env`, passwords or SSH keys.
Generated a101–a108 source changes belong in `optimizations/` or
`scripts/build_experiments.py`, followed by rebuilding and committing the output.

The existing `team_snapshot/` and `citus_project/` directories on Hikaru's Mac
are intentionally ignored; the submitted layout is `citus_project_team_14/`.
