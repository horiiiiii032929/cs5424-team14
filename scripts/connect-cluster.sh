#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
env_file="${script_dir}/../.env"
if [[ -f "$env_file" ]]; then
  # This is a local, trusted shell configuration file. Never enable tracing here.
  source "$env_file"
fi

if [[ $# -gt 1 ]]; then
  echo 'Usage: ./scripts/connect-cluster.sh [SOC_OR_TEAM_USERNAME]' >&2
  exit 2
fi

cluster_user="${1:-${SOC_USER:-}}"
jump_host="${SOC_JUMP_HOST:-stujump.comp.nus.edu.sg}"
login_host="${SOC_LOGIN_HOST:-xlogin.comp.nus.edu.sg}"
if [[ -n "${SOC_PASSWORD:-}" ]]; then
  export SSH_ASKPASS="${script_dir}/cluster-askpass.sh"
  export SSH_ASKPASS_REQUIRE=force
  export DISPLAY="${DISPLAY:-codex}"
fi
if [[ ! "$cluster_user" =~ ^[a-zA-Z0-9._-]+$ || ! "$jump_host" =~ ^[a-zA-Z0-9.-]+$ || ! "$login_host" =~ ^[a-zA-Z0-9.-]+$ ]]; then
  echo 'Set a valid SOC_USER in .env or supply your username as an argument.' >&2
  exit 2
fi

cluster_key="${SOC_SSH_KEY:-${HOME}/.ssh/cs5424_cs14}"
if [[ -f "$cluster_key" ]]; then
  # An explicit ProxyCommand applies the dedicated key to the jump host too.
  exec ssh -i "$cluster_key" -o IdentitiesOnly=yes \
    -o "ProxyCommand=ssh -i '${cluster_key}' -o IdentitiesOnly=yes -W %h:%p '${cluster_user}@${jump_host}'" \
    "${cluster_user}@${login_host}"
fi
exec ssh -J "${cluster_user}@${jump_host}" "${cluster_user}@${login_host}"
