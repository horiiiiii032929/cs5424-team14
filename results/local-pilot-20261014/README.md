# Rejected emulated pilot — do not use for design comparisons

This first timing attempt used the official AMD64 Citus image under emulation
on an ARM Docker host. The one-client baseline completed only five transactions
in the measurement, and the four-client warmup aborted when a worker PostgreSQL
process exited and triggered recovery. No optimized design was timed in this run.

The raw output, environment and worker logs are preserved for diagnosis. The
root cause is not established. A fresh native ARM PostgreSQL 18.6 / Citus 14.1.0
build is used for subsequent runs. Do not combine these timing results with the
native run or the course-cluster baselines.
