# Original course-scale diagnostic — 19 October 2026

Job 977468 ran a101 at scale 1/four clients, 60-second warmup and 60-second
measurement. Both warmup and measurement exited 2. Its partial TPS is not eligible
for comparison. The original post-run global-ID validator then remained active
on the coordinator for over eleven minutes; its query plans and activity snapshot
are in ../cluster/validator-investigation/.

An independent replacement verified the same exact four core invariants on the
full dataset in 25.753 seconds and passed seven deliberate-corruption tests.
Job 977468 was then cancelled to stop the original validator. Dependent jobs
977469/977470 were cancelled before running. The original partial outputs, source
hashes, worker logs and submission ledgers are preserved here. A cancelled job is
not reported as a successfully completed Slurm run.

Remaining candidates were resubmitted from a fresh isolated deployment using the
faster post-measurement validator. Transactions, isolation, workload, logging,
scale and warmup remain unchanged. The revised one-count diagnostic uses its
fresh initial data load without a redundant second load. See ../cluster/ ledgers.
