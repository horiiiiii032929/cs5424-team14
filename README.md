# CS5424 / CS4224 — Team 14

Team: Hikaru, Kelvin, Dessi and Xincheng. Team account: `cs14`.
Submission deadline: **30 October 2026, 23:59 Singapore time**.

This repository holds Dessi's preserved A/B baseline snapshots and Hikaru's
implementations of five proposed Task 2 designs. The proposed work split is
Hikaru + Kelvin on A and Dessi + Xincheng on B.

**27 October status:** The [A report draft](docs/workload-a-report-draft.md)
recommends **a112** as the final A design, and Kelvin supports its selection.
Hikaru's confirmation remains to be recorded, so the recommendation is still
subject to team review. The matched a112 run achieved 16.8–28.2× fresh a0;
the seed-7 repeat's 64-client warmup aborted and remains excluded from clean
comparisons. Kelvin plans to supply his write-side section on 28 October.

Both a115 jobs were fully
[imported and audited](results/cluster-full-a115-20261022/README.md). All 26 runtime
hash comparisons, 24 phase commands/exits, 12 raw-log/transaction-metric counts
and 12 post-run validations are verified. Seven of twelve cases complete both
phases; six also have zero measured failures. Seed-42 c32/c64 and seed-7 c8/c16/c64
measurements abort; both c64 warmups abort. a115 is faster in eligible cases,
but neither seed supplies a clean full matrix.
The [B branch audit](results/b-branch-review-20261022/README.md) is complete;
b6/c16 supports 539.437 TPS, while c8/c32/c64 remain flagged. Final A/B choices
and submission assembly await team review.

See [current status and remaining work](docs/project-status.md),
[verified results](results/README.md), the [A report draft](docs/workload-a-report-draft.md)
and [cluster runbook](docs/workload-a-cluster-runbook.md).
Code and evidence are on [draft PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1);
the a114/a115 merge was into its branch, not into `main`.

## Start here

- [Current status](docs/project-status.md): decisions, evidence and remaining work.
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
Check the live experiment folders and queue with teammates before new submissions.
Both a115 jobs are archived and reviewed; use the evidence and coordinate any necessary new runs.
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
