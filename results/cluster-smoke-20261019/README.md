# Course-cluster smoke results — 19 October 2026

Four jobs ran serially on xcnf0–4 from isolated commit 365eafd. All saved
runtime hashes match the retrieved source and the repository transaction files.
Each case used scale 0.01, five-second warmup and 20-second measurement at
one or four clients, SERIALIZABLE isolation, original A mix, and full logging.
These are course-cluster smoke tests, not the required scale-1 final benchmarks.

| Experiment | Job | 1 client | 4 clients |
|---|---:|---|---|
| a102 control | 977432 | Completed | Completed |
| a101 merchant colocation | 977433 | Completed | Warmup and measurement aborted |
| a111 join-key colocation | 977434 | Completed | Warmup and measurement aborted |
| a112 join-key colocation + READ ONLY | 977435 | Completed | Warmup and measurement aborted |

All eight post-measurement core validation records passed. This does not resolve
the client aborts. Five cases completed both phases; three cases had pgbench exit 2.
Aborted measured TPS is excluded from completed_script_tps in case-review.csv/json.
Raw summaries still contain diagnostic partial values and must not be ranked.

Because this fixture has only one hot merchant, a short scale-1 four-client
diagnostic was scheduled next as jobs 977468–977470 for a101/a111/a112. It retains
the original 60-second warmup and uses a 60-second measurement. Its output is
separate from these smoke results and from any final 600-second measurements.

Original team files and installation were preserved. All job outputs, raw logs,
settings, topology, runtime hashes and validation are in citus_project_team_14/
under this evidence directory; import-manifest.json records retrieval hashes.
