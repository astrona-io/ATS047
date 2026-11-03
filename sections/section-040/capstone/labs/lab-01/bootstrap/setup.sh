#!/usr/bin/env bash
set -euo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-lab-040-capstone-01" ]]; then
  printf 'Refusing to operate on another Kubernetes context\n' >&2
  exit 1
fi
lab_directory="$(cd "$(dirname "$0")/.." && pwd)"
node_name="astro-ats-047-lab-040-capstone-01-control-plane"
worker_name="astro-ats-047-lab-040-capstone-01-worker"
kubectl apply -f "$lab_directory/bootstrap/manifests/start.yaml"
kubectl -n starfleet rollout status deployment/probe --timeout=180s
kubectl -n starfleet wait --for=condition=Ready pod/shuttle --timeout=120s
kubectl -n outpost wait --for=condition=Ready pod/drifter --timeout=120s
kubectl -n starfleet rollout status deployment/prometheus --timeout=180s
kubectl -n starfleet rollout status deployment/traffic --timeout=180s
kubectl -n starfleet rollout status deployment/pushgateway --timeout=180s
kubectl -n starfleet rollout status deployment/receiver --timeout=180s
kubectl -n starfleet exec shuttle -- python -c 'import urllib.request
for group, value in (("old_export", "1700000000"), ("legacy_sync", "1700000500")):
    body = ("lab_batch_last_success_timestamp_seconds " + value + "\n").encode()
    request = urllib.request.Request("http://pushgateway:9091/metrics/job/" + group, data=body, method="PUT")
    urllib.request.urlopen(request, timeout=8).read()'
sleep 12
