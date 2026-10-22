# a115 live readback — 22 October 2026

This is a **transcription of successful tool readbacks in this chat**, not a
complete raw-job import and not an authenticated archive of the remote files.
The earlier 22 October status check successfully read `squeue`, `sacct`, both
`benchmark-results/summary.csv` files, and benchmark/validation excerpts via
`scripts/cluster-command.sh`. These CSV/PSV files preserve the exact displayed
rows. Their local hashes would authenticate this transcription only.

Remote deployment: `/home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae`.
Both jobs finished on 20 October on xcnf0–4. The queue was empty at that successful
22 October check; that snapshot is not a continuing live-state guarantee.

| Clients | Seed 42 TPS | Measured exit | Seed 7 TPS | Measured exit |
|---:|---:|---:|---:|---:|
| 1 | 115.485 | 0 | 109.893 | 0 |
| 4 | 296.697 | 0 | 276.233 | 0 |
| 8 | 335.585 | 0 | 323.378 | 2 |
| 16 | 323.213 | 0 | 325.860 | 2 |
| 32 | 325.640 | 2 | 330.600 | 0 |
| 64 | 366.145 | 2 | 355.620 | 2 |

TPS is raw completed scripts / configured 600 seconds. Measured exits of 2
exclude those cases from clean comparisons even when failed-log counts are zero.
Seed 42/c4 has one recorded serialization failure despite measured exit 0.
Seed 7/c8,c16,c64 record 1/2/7 failed transactions. Validation excerpts contained
`core invariants passed`, but all six blocks per job have not been independently
counted and paired with cases. Warmup exits, complete logs, settings and runtime
hashes remain unreviewed; no case is yet certified fully eligible from this
partial readback. A blanket zero-failure or reliable full-matrix claim is false.

On the subsequent import attempt, SSH timed out during banner exchange (exit
255). The configured VPN service was disconnected; direct xlogin SSH also timed
out. Two full import attempts failed before producing an archive. Reconnect NUS
VPN/network access and run:

```sh
python3 scripts/import_cluster_jobs.py \
  /home/stuproj/cs14/citus_hikaru_20261020-002025_57576ae \
  results/cluster-full-a115-20261022 \
  expt_a115:979909 expt_a115:979910
```

If that destination already contains imported evidence, preserve it and choose
a fresh directory. Review every phase, actual clients, config/topology, runtime
hash, raw transaction count and validation block before promoting a115. a112
remains the provisional A design; the full clean a112 figure is retained.
