#!/usr/bin/env bash
# Copy the committed repository to a new isolated directory; never overwrite team work.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
commit="$(git rev-parse --short HEAD)"
stamp="$(date +%Y%m%d-%H%M%S)"
remote_dir="/home/stuproj/cs14/citus_hikaru_${stamp}_${commit}"
git archive HEAD | "$root/scripts/cluster-command.sh" \
  "umask 077; mkdir '$remote_dir' && tar -xf - -C '$remote_dir'"
echo "Uploaded to $remote_dir"
echo "Run there: bash scripts/submit_cluster.sh smoke"
