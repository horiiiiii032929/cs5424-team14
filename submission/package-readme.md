# CS4224 / CS5424 Team 14 result files

This archive contains the team’s experiment implementations, original cluster
results, and separately identified local validation evidence. A's selected
design is **expt_a112**; a115 is follow-up evidence with aborts, and a10 is a
separate measured implementation. B's combined implementation and comparison
evidence are under **expt_b6**. No a10+a112 combined benchmark is claimed.

## Start here

- `REPRODUCE.md`: running cluster experiments and locating reproduction utilities.
- `experiment-inventory.json`: all 21 top-level folders and their job associations.
- `job-source-map.json`: 45 distinct jobs, canonical experiment ownership, copies,
  and available runtime source-hash matches.
- `supporting-implementation-inventory.json`: eight local-only a103–a110 designs.
- `checksums.sha256`: final file integrity, excluding the checksum file itself.

## Directory and result meanings

Each top-level `expt_aN`/`expt_bN` folder has `run.sh`, nine SQL transactions,
Slurm job output directories and matching `citus-N.out`/`.err` logs.
There are **21 folders and 46 job paths, representing 45 distinct jobs**.
**b201/job-918781** is inherited **b0** baseline evidence, not an additional run.
b201's later jobs remain separately identified. Its original cluster alias is
`expt_xc_b1`; names are preserved in provenance and historical logs.

The brief requires all experiment code and outputs. **b202** (original
`expt_xc_b2`) is retained with jobs 993186 and 994341 even though it was retired
from active development and is not the final B design. **b203/b204** have no
independent benchmark; their source and inherited b2/job-928583 files are under
`supporting_implementations/retired/`, explicitly excluded from experiment/job
counts. Historical aliases and source provenance remain available.
Supplementary b0/b6 results are under each experiment's `slurm-results/`;
their original `supplementary-results/` paths remain in provenance.

Failed and cancelled attempts remain intact. Some have no measurement CSV.
Some measured cases have zero failed log records but a nonzero pgbench exit.
Check warmup and measurement exits, retries, failed records and configuration
before comparing TPS. Job 1031186 is a separate b6 correctness run, not a
replacement for the full performance matrix. Slurm COMPLETED is not proof of
a clean benchmark. Historical, diagnostic, local and full-scale timings differ.

## Supporting evidence and provenance

`supporting_implementations/local_only/` holds a103–a110; these have no recorded
Slurm benchmark. `evidence/local-only/` contains local correctness suites,
validator checks and pilots, including failed stress cases. These timings do
not establish course-cluster performance. Historical evidence READMEs retain
original-repository links; resolve such links via `REPRODUCE.md`.

`source_snapshots/` directories preserve earlier code. Only 15 jobs have runtime
hash manifests; other jobs' source identity is not hash-certified. The source
map locates exact archived code where hashes exist, including old validators.

In `packaging-provenance.json`, `source_sha256` (and legacy `sha256`) identifies
the original copied source; `packaged_sha256` identifies the final destination.
`destination_modified` marks packaging README edits or the installer email
change. `checksums.sha256` is the authoritative final archive byte manifest.

The configured installer is included. Its original starter copy is retained
under `source_snapshots/original-installer/`. Installation replaces `$HOME/pgsql`;
reuse the existing course installation unless a new installation is needed.
Eight Hikaru runners intentionally disable notification mail; this does not
change benchmark execution.
