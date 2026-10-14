# Results

## Existing course-cluster baselines

- A: `../citus_project_team_14/expt_a0/slurm-results/job-918524/benchmark-results/`
- B: `../citus_project_team_14/expt_b0/slurm-results/job-918781/benchmark-results/`

These are preserved team results, not new optimized runs. Workload A at one
client achieved 3.220 TPS; average T3 latency was 2678.797 ms. Baseline A contains
serialization failures at 16/32/64 clients. Baseline B includes pgbench exit 2
at 8/16 clients; investigate those failures before using them as clean comparisons.

## New implementation validation

Validation and local pilot results are being collected. Their `environment.json`
records versions, data scale and settings. Local Docker and SoC Slurm results
must not be compared as if they used the same hardware or dataset.

As of setup on 14 October 2026, SoC SSH timed out before authentication. No new
Slurm job has been submitted, and no optimized course-cluster result is claimed.
