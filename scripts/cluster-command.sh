#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$script_dir/../.env" ]]; then source "$script_dir/../.env"; fi
cluster_user="${SOC_USER:-cs14}"
jump_host="${SOC_JUMP_HOST:-stujump.comp.nus.edu.sg}"
login_host="${SOC_LOGIN_HOST:-xlogin.comp.nus.edu.sg}"
if [[ ! "$cluster_user" =~ ^[a-zA-Z0-9._-]+$ || ! "$jump_host" =~ ^[a-zA-Z0-9.-]+$ || ! "$login_host" =~ ^[a-zA-Z0-9.-]+$ ]]; then
  echo 'Invalid SSH destination in .env' >&2; exit 2
fi
export SSH_ASKPASS="$script_dir/cluster-askpass.sh" SSH_ASKPASS_REQUIRE=force
export DISPLAY="${DISPLAY:-codex}"
# SSH consumes the password through askpass; it never enters argv or logs.
exec ssh -o ConnectTimeout=15 -o NumberOfPasswordPrompts=1 \
  -J "$cluster_user@$jump_host" "$cluster_user@$login_host" "$@"
