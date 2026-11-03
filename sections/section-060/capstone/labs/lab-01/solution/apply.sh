#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-capstone-060" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
solution_directory="$lab_directory/solution"
node_name="astro-ats-047-capstone-060-control-plane"
worker_name="astro-ats-047-capstone-060-worker"

kubectl -n starfleet create configmap prometheus-rules \
  --from-file=rules.yaml="$solution_directory/rules.yaml" \
  --dry-run=client -o yaml | kubectl apply -f -
kubectl -n starfleet rollout restart deployment/prometheus
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
