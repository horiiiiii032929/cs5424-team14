# Native local database fixture

The upstream `citusdata/citus:14.1.0` image resolved to AMD64. A baseline warmup
crashed in an emulated worker on this ARM Mac, so timing from that attempt is
excluded. The exact root cause has not been established.

This Dockerfile compiles the official Citus v14.1.0 source on the cached native
ARM PostgreSQL 18.6 base, with pinned base digest and source SHA-256. The test
runner records the resulting image ID and full server versions. It builds only
inside Docker; the Mac and course-cluster PostgreSQL installations are untouched.

The Compose project is `cs5424-hikaru`, isolated from other Docker projects. No
database ports are exposed to the host. Temporary databases can be discarded with
`docker compose down --volumes` after saving results.

The source/configuration are intended for development tests. The official SoC
benchmark is run with the self-contained Slurm scripts in the experiment folders.
