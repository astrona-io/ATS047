#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-playground-020-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
for attempt in $(seq 1 20); do
  if bash "$lab_directory/validate.sh"; then exit 0; fi
  sleep 3
done
printf 'Playground did not become ready within the bounded retry period\n' >&2
exit 1
