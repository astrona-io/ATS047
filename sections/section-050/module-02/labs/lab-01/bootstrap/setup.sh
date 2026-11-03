#!/usr/bin/env bash
# Starting state: namespaces starfleet and outpost, the probe and scout metrics
# workloads, a traffic generator, and a Prometheus server with its own
# ServiceAccount and read access to pods. Environment only; the learner changes
# the Prometheus configuration.
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-lab-050-02-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
directory="$(cd "$(dirname "$0")/.." && pwd)"
kubectl apply -f "$directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet rollout status deployment/scout --timeout=180s
kubectl -n starfleet rollout status deployment/traffic --timeout=180s
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost wait --for=condition=Ready pod/drifter --timeout=120s
sleep 12
