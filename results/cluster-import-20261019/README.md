# Verified Kelvin cluster results — retrieved 19 October 2026

SSH access was restored on 19 October. This read-only import preserves Kelvin's
five experiment folders from `/home/stuproj/cs14/citus_project`, with original
scripts, SQL, runtime source hashes, raw transaction logs, PostgreSQL diagnostics,
validation and Slurm output. `import-manifest.json` records retrieval time and
SHA-256 hashes. Kelvin owns these runs; Hikaru retrieved and reviewed the files.
No existing cluster files were modified by the import.

## a102 — job 965657

All 12 run.sh/transaction/supporting SQL files match the repository's preserved
82058e6 source. The saved runtime `code-sha256.txt` also matches the downloaded
source. Topology was xcnf1 coordinator with xcnf2–5 workers. The recorded software
is PostgreSQL 18.6/Citus 14.1.0 on x86_64. Scale, workload mix, SERIALIZABLE
isolation, retries, logging, 60-second warmup and 600-second measurement match
the preserved baseline configuration. Nodes differ within the xcnf family.

| Clients | Baseline a0 TPS | a102 TPS | Observed gain | Serialization failures a0 → a102 |
|---:|---:|---:|---:|---:|
| 1 | 3.220 | 3.250 | 0.93% | 0 → 0 |
| 4 | 2.283 | 3.453 | 51.25% | 0 → 0 |
| 8 | 2.285 | 3.543 | 55.05% | 0 → 0 |
| 16* | 2.368 | 3.320 | 40.20% | 25 → 0 |
| 32 | 2.405 | 3.782 | 57.26% | 51 → 0 |
| 64 | 2.283 | 3.398 | 48.84% | 50 → 0 |

All six **measured-phase** pgbench exit codes are zero. The 16-client warmup
exited 2 before its completed measurement; flag that observation and exclude it
from clean-run comparisons. Other a102 warmups exited zero. The validation log
contains six passing core invariant checks. The observed four-client-upward gain is **40–57%** in these
files, refining the teammate message's approximate 40–65% range. These are
single-run comparisons, not confidence estimates or repeated-run findings.

At one client, T3/T4 average latency is 2668.472/454.362 ms, barely changed from
baseline 2678.797/458.862 ms. T7 falls from 51.114 to 13.709 ms. This supports
continuing the placement investigation rather than more short-write tuning.

## Kelvin's write-side experiments

| Experiment | Job | Change relative to a102 | Review |
|---|---|---|---|
| a10 | 966308 | Autocommit T2/T5/T8/T9 | 32-client run has pgbench exit 2; exclude its partial TPS. |
| a11 | 967195 | fillfactor 80 | All six exits zero; no consistent TPS improvement over a102. |
| a12 | 967217 | synchronous_commit off | All six exits zero; no consistent material TPS improvement; durability tradeoff remains. |
| a14 | 967194 | VACUUM only | All six exits zero; one recorded serialization failure at 32 clients. |

All five jobs contain six passing core validation records. This does not make an
aborted phase eligible for a clean-run comparison. `case-review.csv`/`.json`
enumerate all 30 cases and leave eligible TPS empty for a10/c32 (measured abort)
and a102/c16 (warmup abort). The original measured TPS is preserved separately;
only a10/c32's measured TPS is a partial diagnostic. Twenty-eight cases completed
both phases; their failures/retries remain visible. These write variants are not
selected as final designs.
