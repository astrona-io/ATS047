#!/usr/bin/env bash
# Check: the running Prometheus configuration has a job pods with kubernetes_sd_configs.
set -uo pipefail
if [[ "$(kubectl config current-context)" != "kind-astro-ats-047-lab-050-01-01" ]]; then
  echo "FAIL: wrong Kubernetes context" >&2
  exit 1
fi
prom_get() {
  kubectl -n starfleet exec shuttle -- python -c 'import sys, urllib.parse, urllib.request
url = "http://prometheus:9090" + sys.argv[1]
print(urllib.request.urlopen(url, timeout=8).read().decode())' "$1"
}
for attempt in $(seq 1 12); do
  if prom_get '/api/v1/status/config' | python3 -c 'import json, sys
text = json.load(sys.stdin)["data"]["yaml"]
assert "job_name: pods" in text and "kubernetes_sd_configs" in text and "role: pod" in text' 2>/dev/null; then
    echo "PASS: the job pods uses kubernetes_sd_configs with the pod role"
    exit 0
  fi
  sleep 5
done
echo "FAIL: the running configuration has no job pods with kubernetes_sd_configs and role pod; apply the ConfigMap and restart the prometheus Deployment"
exit 1
