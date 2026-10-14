#!/usr/bin/env bash
# Run on xlogin from the cloned repository, after checking experiment IDs.
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mode="${1:-smoke}"
case "$mode" in smoke|full) ;; *) echo 'Usage: scripts/submit_cluster.sh smoke|full' >&2; exit 2;; esac
command -v sbatch >/dev/null
mkdir -p "$root/results/cluster"
ledger="$root/results/cluster/submissions-$(date +%Y%m%d-%H%M%S).tsv"
printf 'experiment\tmode\tjob_id\n' > "$ledger"
# Same team port: depend on every existing team job, then serialize this suite.
dependency="$(squeue -h -u "$USER" -o '%A' | sort -u | paste -sd: -)"
dependency_kind=afterany
for expt in expt_a0 expt_a101 expt_a102 expt_a103 expt_a104 expt_a105 expt_a106 expt_a107 expt_a108; do
  dir="$root/citus_project_team_14/$expt"
  bash -n "$dir/run.sh"
  args=(--parsable --mail-type=NONE --job-name="team14-hikaru-$mode")
  if [[ -n "$dependency" ]]; then args+=(--dependency="$dependency_kind:$dependency"); fi
  if [[ "$mode" == smoke ]]; then
    args+=(--export=ALL,SCALE=0.01,DURATION=20,WARMUP_DURATION=5,CLIENT_COUNTS=1,PROGRESS_INTERVAL=5)
  else
    args+=(--export=ALL,SCALE=1,DURATION=600,WARMUP_DURATION=60)
  fi
  job="$(cd "$dir" && sbatch "${args[@]}" run.sh)"
  job="${job%%;*}"
  [[ "$job" =~ ^[0-9]+$ ]] || { echo "Unexpected sbatch response: $job" >&2; exit 1; }
  printf '%s\t%s\t%s\n' "$expt" "$mode" "$job" | tee -a "$ledger"
  dependency="$job"
  dependency_kind=afterok
done
echo "Saved submission ledger: $ledger"
