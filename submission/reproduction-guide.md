# Running and interpreting the submitted files

## Course-cluster entry points

Extract the ZIP and use the existing PostgreSQL 18.6 / Citus 14.1.0 installation
at `$HOME/pgsql`. Inspect the queue before running: these scripts default to
team 14 and share port 5446. Run one experiment at a time. From the extracted root:

```sh
cd expt_a112
sbatch run.sh
```

For B use `expt_b6`. Baselines are `expt_a0` and `expt_b0`. Review each runner's
defaults and the intended historical job's `benchmark-results/config.txt`.
Reproducing a particular result may require its recorded seed, client counts,
duration, workload weights, resets, hardware allocation and source snapshot.
Defaults alone do not reproduce every stored job. Do not use inherited
b203/b204 results as measurements of those source variants.

Look in `slurm-results/job-N/benchmark-results/` for config, summary and
per-transaction CSVs, textual warmup/result files and raw transaction logs.
Database, schema, topology and validation logs are one directory above.
Keep the Slurm `citus-N.out` and `.err` files in the experiment directory.

## Separate b6 correctness harness

The preserved 28 October source snapshot contains `run_correctness.sh`,
`correctness.sql` and its transaction directory. Submit from that directory
so that Slurm's submit directory and all relative dependencies agree:

```sh
cd expt_b6/source_snapshots/live-readback-20261028
sbatch run_correctness.sh
```

This is a separate, shorter correctness run with before/after checks and a
controlled T7 conservation check. Its historical successful job is 1031186;
1031165 is an earlier failed attempt. Do not treat these as a full workload matrix.

## Archived local analysis utilities

`analysis_scripts/` is source reference material from the repository. Those
scripts assume the original repository layout and are **not directly runnable
from their relocated ZIP paths**. The core Slurm experiments are self-contained
and do not call these analysis utilities.

For local validation tooling, obtain the repository, use its root as the working
directory, and follow its Docker README and script arguments:

```sh
git clone https://github.com/horiiiiii032929/cs5424-team14.git
cd cs5424-team14
git checkout 497d82b794ec74c4e4d5bd72d354639d01c7c81d
python3 scripts/check_correctness.py --help
```

This identifies the repository revision present at the audit. It provides
`compose.yaml`, `docker/`, `optimizations/`, `scripts/` and the expected
`citus_project_team_14/` tree. Docker and the dependencies documented there are
needed for actual local runs. Local setup scripts create/reset their test
database. A repository checkout or today's source is not proof of historical
runtime identity; consult the source map and job manifests.

## Historical evidence paths

Original evidence READMEs have been preserved and may link to their original
repository locations. The packaged equivalents are:

| Original repository path | Packaged path |
|---|---|
| `results/<cluster-collection>/` review files | `evidence/<cluster-collection>/` |
| `results/<local-suite>/` | `evidence/local-only/<local-suite>/` |
| A/B Slurm raw results across collections | `<experiment>/slurm-results/job-N/` |
| Earlier experiment code | `<experiment>/source_snapshots/` |
| a103–a110 local-only implementations | `supporting_implementations/local_only/<experiment>/` |

The added read-only, join-placement and scalable-validator suites are local
supporting evidence. For links outside these packaged paths, use the repository
checkout; no missing historical result has been fabricated.

## Integrity

From the extracted archive root, run `sha256sum -c checksums.sha256` on Linux.
`job-source-map.json` distinguishes runtime hashes from current readback hashes.
The copied jobs have canonical owners; count each Slurm job/client pair once.
