# Cluster setup

The official starter files are downloaded into `citus_project/`. Database installation and benchmark execution belong on the SoC Slurm cluster.

## Verified account and prerequisites

- Confirmed project team account: `cs14`.
- Confirmed team number: 14; the local experiment scripts default to 14 (port 5446).
- Existing team directory: `/home/stuproj/cs14/citus_project`.
- NUS VPN connection when accessing the cluster from outside NUS.

## Connect

Enable SoC Compute Cluster access in MySoC first. Connect to NUS VPN if outside NUS, then run from this workspace:

```bash
./scripts/connect-cluster.sh
```

Enter authentication credentials in the terminal when prompted. The course guide requires SSH public keys when connecting from within NUS without VPN.

The helper loads account and host settings from the private local `.env` file. `.env` is excluded from Git and restricted to your user. When `SOC_PASSWORD` is filled in, a private SSH askpass helper supplies it to SSH without placing it in command-line arguments. Otherwise SSH prompts in the terminal.

## Check the existing team setup

After connecting, these commands inspect the shared account without changing its installation:

```bash
pwd
ls -ld "$HOME/pgsql" "$HOME/citus_project"
"$HOME/pgsql/bin/psql" --version
"$HOME/pgsql/bin/pgbench" --version
squeue -u "$USER"
```

Use the project directory Dessi provides if it differs from `$HOME/citus_project`. Review existing `expt_a0/` and `expt_b0/` outputs before scheduling new baseline runs.

## Configure scripts before a new job

In each experiment's `run.sh`, verify `TEAM_ID` is 14 and check the notification email in `#SBATCH --mail-user`. Set the notification email in `install_citus_slurm.sh` if an installation is needed.

The provided installer removes `$HOME/pgsql` before rebuilding it. Reuse an existing working team installation; check with the team before replacing it, especially if another job is running.

Keep `LOG_SAMPLE_RATE=1.0`; the downloaded script explicitly says this value must not change. Keep baseline scripts and results as the comparison for later optimization experiments.

Submit a benchmark from its experiment directory, on the cluster:

```bash
cd expt_a0
sbatch run.sh
squeue -u "$USER"
```

## Existing benchmark results

For each experiment, inspect:

```text
expt_a0/slurm-results/job-<id>/benchmark-results/summary.csv
expt_a0/slurm-results/job-<id>/benchmark-results/transaction_metrics.csv
```

The same structure applies to `expt_b0` and later experiments. Also preserve `config.txt`, server version and topology records, PostgreSQL logs, and Slurm output/error files.

## Current setup and access status — 20 October 2026

Team account `cs14` and installation `/home/stuproj/cs14/pgsql` were verified.
Baseline jobs 918524/918781 record PostgreSQL 18.6 and Citus 14.1.0. Cluster
scripts use TEAM_ID 14 / port 5446 and passed the cluster's Bash syntax checks.
This Mac's system Bash 3.2 cannot validate their modern Bash features.

SSH worked on 19 October and benchmarks used isolated deployments, preserving
`/home/stuproj/cs14/citus_project` and the existing installation. The 20 October
reconciliation timed out before login; live queue state could not be checked.
Do not treat old statements about an empty queue as current.

Latest deployment: `/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae`.
Full a115 jobs 979909/979910 were submitted there and await retrieval/review.
See the [runbook](docs/workload-a-cluster-runbook.md) for exact queue/accounting
and import commands, and [current project status](docs/project-status.md) for
completed a0/a112 results and remaining work. Check these jobs before resubmitting.

A dedicated SSH key was created at `~/.ssh/cs5424_cs14` with public key
`~/.ssh/cs5424_cs14.pub`; its registration was not verified. The successful
recorded connection used password authentication with the network/VPN setup.
If public-key authentication is required, use SoC's registration instructions.

`bash scripts/upload_cluster.sh` copies committed files into a fresh isolated
directory. Coordinate job order and inspect the shared queue before submissions;
all team experiments share port 5446. Keep complete raw outputs, code hashes,
settings, topology, validation and failure logs.
