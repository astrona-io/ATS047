#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-playground-040-02" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
node_name="astro-ats-047-playground-040-02-control-plane"
worker_name="astro-ats-047-playground-040-02-worker"

python3 "$solution_directory/record.py"
