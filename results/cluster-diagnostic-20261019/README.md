# Revised scale-1 diagnostics — 19 October 2026

All three jobs ran on xcnf0–4 with scale 1, four clients, SERIALIZABLE isolation,
original A weights, a 60-second warmup and a 60-second measurement. Each used
its fresh initial dataset and skipped a redundant reload for this single count.
These are diagnostics, not the final six-client 600-second benchmarks.

| Experiment | Job | Completed scripts | Count / 60 s TPS | pgbench elapsed TPS | p95 ms | p99 ms |
|---|---:|---:|---:|---:|---:|---:|
| expt_a111 | 977617 | 5395 | 89.917 | 89.347 | 57.300 | 820.622 |
| expt_a112 | 977618 | 5543 | 92.383 | 91.951 | 61.495 | 780.407 |
| expt_a113 | 977619 | 5433 | 90.550 | 89.755 | 82.741 | 803.896 |

All warmup and measured exit codes are zero. Each measured case records zero
failed log records, serialization failures and retries. Each exact post-run
validator completed and passed. Saved runtime hashes match the retrieved code,
and config.txt verifies the intended scale, client count, timing and resets.

This differs from the scale-0.01 smoke failures; those failures remain preserved.
One short observation per variant does not establish a ranking or confidence.
a112 advances as a candidate for the full comparison against a fresh original
a0 control; no final design is selected.

Full jobs: a0 control 977740 and a112 candidate 977773, serialized with the same
requested xcnf0–4 node list. They restore the original six client counts,
600-second measurements, 60-second warmup and data resets, seed 42 and full
logging. Full outputs are still pending and are not mixed into this table.
Pending job 977741 was replaced before starting to correct its explicit node
request; the submission/correction records are in `../cluster/`.

The deployment uses cf48c8d experiment source and the revised submission helper.
Source, settings, logs and validation are preserved here; import-manifest.json
records exact retrieval hashes. The faster validator is post-measurement only.
