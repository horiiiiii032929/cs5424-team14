#!/usr/bin/env bash
set -euo pipefail

# SSH invokes this helper privately; never run it directly or enable tracing.
case "${1:-}" in
  *[Pp]assword:*) ;;
  *) exit 1 ;;
esac

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
source "${script_dir}/../.env"
[[ -n "${SOC_PASSWORD:-}" ]] || exit 1
printf '%s\n' "$SOC_PASSWORD"
