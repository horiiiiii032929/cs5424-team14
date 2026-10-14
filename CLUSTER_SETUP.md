# Cluster setup

The official starter files are downloaded into `citus_project/`. Database installation and benchmark execution belong on the SoC Slurm cluster.

## Information still needed

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

In each experiment's `run.sh`, set the real team number in `TEAM_ID=${TEAM_ID:-99}` and the notification email in `#SBATCH --mail-user`. Set the notification email in `install_citus_slurm.sh` if an installation is needed.

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

## Setup status

Completed locally: downloaded and extracted official starter files; added the SSH connection helper; checked the helper and installer with Bash; downloaded the team's baseline scripts, outputs and logs to `team_snapshot/`.

The benchmark scripts use modern Bash features (`declare -A` and `[[ -v ... ]]`) that this Mac's Bash 3.2 does not support. Their syntax must be checked with the cluster's newer Bash before execution.

Verified remote access through `stujump.comp.nus.edu.sg` to `xlogin.comp.nus.edu.sg` as `cs14`. Account home: `/home/stuproj/cs14`. Existing project: `/home/stuproj/cs14/citus_project`. Existing installation: `/home/stuproj/cs14/pgsql`.

A dedicated SSH key was created at `~/.ssh/cs5424_cs14`, with public key `~/.ssh/cs5424_cs14.pub`. It has not been registered. The verified connection used password authentication with the current network/VPN setup. If connecting without NUS VPN requires public-key authentication, register this public key using SoC's key-registration instructions.

Verified versions in both baseline jobs: PostgreSQL 18.6 and Citus 14.1.0. Both remote benchmark scripts pass the cluster's Bash syntax check and use TEAM_ID 14 and PGPORT 5446. Existing notification email settings were retained. No Slurm jobs were queued at inspection time.

Baseline A: `expt_a0/slurm-results/job-918524/benchmark-results/`.
Baseline B: `expt_b0/slurm-results/job-918781/benchmark-results/`.

The remote repository has local Git commit `5dcb908` and no configured remote. The two `run.sh` files have uncommitted team-specific changes, and result files are untracked. These were preserved; no remote Git changes, reinstallations, or new benchmark jobs were performed.

Next: review baseline failures before optimization comparisons. A has non-zero failed-log-record counts at 16, 32 and 64 clients. B has non-zero counts from 4 clients onward, and pgbench exit code 2 at 8 and 16 clients. Existing results are available locally for that review.

## 14 October implementation update

Hikaru's private repository is https://github.com/horiiiiii032929/cs5424-team14.
The latest connection attempts timed out before authentication; the verified
remote information above is the earlier snapshot, not a fresh inspection.

`scripts/cluster-command.sh 'squeue -u cs14'` tests access without exposing the
password. Once connected, `scripts/upload_cluster.sh` copies committed files into
a new isolated remote directory. It does not overwrite Dessi's working directory
or change the existing installation. Run `scripts/submit_cluster.sh smoke` from
that directory, inspect the smoke jobs, and only then submit the full suite.
