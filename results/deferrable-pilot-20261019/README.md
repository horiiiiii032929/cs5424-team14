# READ ONLY DEFERRABLE pilot — 19 October 2026

a113 passed 29 dedicated correctness checks, but its native Docker four-client
pilot aborted in the five-second warmup. No 45-second measurement was started.
The error includes a T2 distributed shard-commit failure after a worker
serialization conflict. All five post-failure invariants passed.

The new access mode did not resolve this local failure. No TPS is eligible for
comparison. Preserve raw warmup output, failure.json, settings and code hashes;
SUMMARY.md and comparison.csv exclude failed timing metrics.

The environment, workload and fixture match the preceding scale-0.01 local
tests, except for the explicit read-only DEFERRABLE declaration. This keeps
SERIALIZABLE isolation and permits snapshot waiting rather than weakening
isolation. No cluster run of a113 is claimed here.
