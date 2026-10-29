# CS5424 / CS4224 — Team 14

Team: Hikaru, Kelvin, Dessi and Xincheng. Team account: `cs14`.
Submission deadline: **30 October 2026, 23:59 Singapore time**.

**29 October handoff:** The modular LaTeX review draft is **19 pages**.
The Overleaf source ZIP and three Canvas artifacts are prepared locally.
See [the teammate handoff](docs/team-handoff-2026-10-29.md) for the exact files,
owners and remaining checks. Team review and AI-record completeness are still
pending; no Canvas upload is recorded.

**A is agreed:** a112 is the final measured design; a115 stays follow-up with
abort caveats; a10 is separate and was not benchmarked on top of a112.
Kelvin's write-path analysis is incorporated. The B pair must confirm their
final design, attribution and evidence wording.

Use the [shared Overleaf project](https://www.overleaf.com/project/6ae2d836f7dbb8dab0442621) for final report
edits. Hikaru supplied this project on 29 October; its contents have not been
synchronized or compared with the local draft in this cleanup. Keep reviewed
source snapshots in [submission/report/](submission/report/). Use
`bash scripts/build_report.sh` to build the local PDF and portable source ZIP.
Follow [CONTRIBUTING.md](CONTRIBUTING.md) for peer review.

Code and evidence were merged into `main` through
[PR #1](https://github.com/horiiiiii032929/cs5424-team14/pull/1) on 29 October.
Review the remaining report cleanup in [PR #4](https://github.com/horiiiiii032929/cs5424-team14/pull/4).
The branch is `codex/maintainable-latex-report`; PR #3 is superseded by #4.
See [the dated evidence status](docs/project-status.md) and
[results](results/README.md) for the audit history and comparison limitations.

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
