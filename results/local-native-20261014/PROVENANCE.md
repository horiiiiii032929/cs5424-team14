# Pilot provenance

This directory contains the native ARM pilot attempted on 14 October 2026.
The matrix contains a0 and a101–a108, each at one and four clients. Sixteen cases
completed and two aborted. Failed cases are retained, not replaced by retries.

The suite initially stopped at the a101 four-client warmup failure. The driver
was updated to record failures, check integrity afterward and continue the
remaining independent cases. Completed cases were not rerun. The update changed
failure handling and reporting, not the transaction SQL or benchmark settings.

`environment.json` records the environment at the resumed invocation. Its Git
commit is HEAD at that invocation and can precede the harness commit. The saved
`harness_snapshot.py` matches `harness_sha256`; per-case `code-sha256.json` records
the exact SQL and Slurm script used. Each case also records its effective settings
and dataset dimensions. Native Docker build output is in `../native-build-20261014/`.

`metrics.json` in a failed case contains diagnostic partial measurements, not a
valid comparison result. Use `failure.json` and pgbench's exit status alongside
any metrics. The generated comparison excludes failed throughput. A status of
`passed` means pgbench exited successfully and the recorded integrity checks
passed; it is not a claim of statistical confidence or production readiness.

`docker.log` contains service diagnostics collected after the full matrix.
All measured runs used serializable isolation. The tuning experiments' effective
memory and pool values were checked before measurement.
